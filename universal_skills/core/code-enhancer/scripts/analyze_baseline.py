#!/usr/bin/env python3
"""Baseline-aware debt tracking for the code-enhancer skill.

Gives every finding a stable, content-derived *fingerprint* so a run can be
compared against a saved *baseline* snapshot and classify each finding as
``new`` / ``persisting`` / ``fixed``. That turns the absolute 0-100 score into a
CI-friendly gate: teams can "fail only on **new** debt" while paying down legacy
debt over time, instead of being blocked by a low score they inherited.

Fingerprints are line-number independent (so moving code does not invent new
debt) and count-normalized (numeric tokens collapse to ``#`` so a summary like
"3 HIGH vulnerabilities" matching "5 HIGH vulnerabilities" is the *same* finding,
not a new one). The detector is deterministic — no LLM, no network — like the
other code-enhancer analyzers.

Inputs accepted (auto-detected):
  * an ``enhance_repo.py`` aggregate ``{repo, domains: {key: {...}}}``
  * a ``generate_report.py`` style list ``[{domain, findings, ...}, ...]``

CONCEPT:CE-039 — Baseline-aware "fail only on new debt"

Usage:
    python analyze_baseline.py <report.json> --write-baseline .ce-baseline.json
    python analyze_baseline.py <report.json> --baseline .ce-baseline.json [--json]
    python analyze_baseline.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from typing import Any, Iterable

BASELINE_VERSION = 1
_NUM_RE = re.compile(r"\d+")
_WS_RE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    """Lowercase, collapse whitespace, and mask numbers so count drift in a
    summary string ("3 errors" vs "5 errors") does not read as a new finding."""
    masked = _NUM_RE.sub("#", str(text))
    return _WS_RE.sub(" ", masked).strip().lower().rstrip(".")


def fingerprint(domain: str, label: str, file: str | None = None) -> str:
    """Stable 16-hex content hash over (domain, normalized label, file basename).

    Line numbers are intentionally excluded; the file is reduced to its basename
    so the same issue keeps its identity across machines and after code moves.
    """
    base = os.path.basename(file) if file else ""
    payload = f"{domain}\x1f{_normalize(label)}\x1f{base.lower()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def _iter_domain_results(report: Any) -> Iterable[dict[str, Any]]:
    """Yield per-domain result dicts from either supported input shape."""
    if isinstance(report, list):
        for item in report:
            if isinstance(item, dict):
                yield item
    elif isinstance(report, dict) and isinstance(report.get("domains"), dict):
        for key, val in report["domains"].items():
            if isinstance(val, dict):
                # enhance_repo aggregate omits the human domain name; supply the key.
                yield {"domain": val.get("domain", key), **val}
    elif isinstance(report, dict) and "findings" in report:
        yield report  # a single domain result


def extract_units(report: Any) -> list[dict[str, Any]]:
    """Flatten a report into fingerprintable finding *units*.

    Two granularities are captured: the human-readable ``findings`` strings each
    domain emits, and — when present — the structured ``vulnerabilities`` list
    (so security debt is tracked per CWE+file, not just per summary line).
    """
    units: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _add(domain: str, label: str, file: str | None, severity: str | None) -> None:
        fp = fingerprint(domain, label, file)
        if fp in seen:
            return
        seen.add(fp)
        unit = {"fingerprint": fp, "domain": domain, "label": str(label)[:200]}
        if file:
            unit["file"] = os.path.basename(file)
        if severity:
            unit["severity"] = severity
        units.append(unit)

    for result in _iter_domain_results(report):
        domain = str(result.get("domain", "unknown"))
        for finding in result.get("findings", []) or []:
            if isinstance(finding, str):
                _add(domain, finding, None, None)
            elif isinstance(finding, dict):
                _add(
                    domain,
                    finding.get("title")
                    or finding.get("detail")
                    or json.dumps(finding),
                    finding.get("file"),
                    finding.get("severity"),
                )
        for vuln in result.get("vulnerabilities", []) or []:
            if isinstance(vuln, dict):
                label = f"{vuln.get('cwe', '')} {vuln.get('name', '')}".strip()
                _add(
                    domain,
                    label or "vulnerability",
                    vuln.get("file"),
                    vuln.get("severity"),
                )
    return units


def _scores(report: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for result in _iter_domain_results(report):
        if isinstance(result.get("score"), (int, float)):
            out[str(result.get("domain", "unknown"))] = result["score"]
    return out


def snapshot(report: Any, *, now: str | None = None) -> dict[str, Any]:
    """Build a baseline snapshot: the fingerprint set + per-domain scores."""
    units = extract_units(report)
    return {
        "version": BASELINE_VERSION,
        "created": now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fingerprints": {u["fingerprint"]: u for u in units},
        "scores": _scores(report),
    }


def diff(report: Any, baseline: dict[str, Any]) -> dict[str, Any]:
    """Classify findings in ``report`` against a ``baseline`` snapshot."""
    base_fps = set((baseline or {}).get("fingerprints", {}).keys())
    units = extract_units(report)
    cur_fps = {u["fingerprint"] for u in units}

    new = [u for u in units if u["fingerprint"] not in base_fps]
    persisting = [u for u in units if u["fingerprint"] in base_fps]
    fixed = [baseline["fingerprints"][fp] for fp in base_fps - cur_fps]
    # New-debt gate score: 100 minus weighted new findings (High weighs more).
    weight = {"High": 8, "Critical": 12, "Medium": 4, "Low": 2}
    penalty = sum(weight.get(u.get("severity", ""), 3) for u in new)
    new_debt_score = max(0, 100 - penalty)
    return {
        "new": new,
        "persisting": persisting,
        "fixed": fixed,
        "counts": {"new": len(new), "persisting": len(persisting), "fixed": len(fixed)},
        "new_debt_score": new_debt_score,
        "clean": len(new) == 0,
    }


def to_markdown(diff_result: dict[str, Any]) -> str:
    """Render the new/fixed sections for inclusion in the enhancement report."""
    c = diff_result["counts"]
    lines = [
        "## 🆕 Baseline Diff — New Debt This Run",
        "",
        f"**New-debt score: {diff_result['new_debt_score']}/100** · "
        f"🆕 {c['new']} new · 🔁 {c['persisting']} persisting · ✅ {c['fixed']} fixed",
        "",
    ]
    if diff_result["new"]:
        lines += ["### New findings (gate these)", ""]
        for u in diff_result["new"][:30]:
            loc = f" `{u['file']}`" if u.get("file") else ""
            sev = f" _{u['severity']}_" if u.get("severity") else ""
            lines.append(f"- **[{u['domain']}]**{sev} {u['label']}{loc}")
        lines.append("")
    else:
        lines += ["_No new debt introduced relative to the baseline._", ""]
    if diff_result["fixed"]:
        lines += ["### Resolved since baseline", ""]
        for u in diff_result["fixed"][:15]:
            lines.append(f"- ~~[{u['domain']}] {u['label']}~~")
        lines.append("")
    return "\n".join(lines)


def _self_test() -> int:
    base_report = [
        {
            "domain": "Security Analysis",
            "score": 70,
            "findings": ["3 HIGH severity vulnerabilities found"],
            "vulnerabilities": [
                {
                    "cwe": "CWE-78",
                    "name": "OS Command Injection",
                    "file": "/a/b/run.py",
                    "line": 10,
                    "severity": "High",
                },
            ],
        }
    ]
    snap = snapshot(base_report, now="2026-01-01T00:00:00Z")
    assert snap["fingerprints"], "snapshot empty"

    # Same finding, count changed + line moved → must classify as persisting, not new.
    moved = [
        {
            "domain": "Security Analysis",
            "score": 70,
            "findings": ["5 HIGH severity vulnerabilities found"],
            "vulnerabilities": [
                {
                    "cwe": "CWE-78",
                    "name": "OS Command Injection",
                    "file": "/a/b/run.py",
                    "line": 42,
                    "severity": "High",
                },
            ],
        }
    ]
    d = diff(moved, snap)
    assert d["counts"]["new"] == 0, f"count/line drift leaked as new: {d['counts']}"
    assert d["counts"]["persisting"] == 2, d["counts"]

    # A genuinely new finding shows up as new; the removed one shows as fixed.
    changed = [
        {
            "domain": "Security Analysis",
            "score": 50,
            "findings": ["1 MEDIUM severity vulnerabilities found"],
            "vulnerabilities": [
                {
                    "cwe": "CWE-94",
                    "name": "Code Injection",
                    "file": "/a/b/eval.py",
                    "line": 3,
                    "severity": "High",
                },
            ],
        }
    ]
    d2 = diff(changed, snap)
    assert d2["counts"]["new"] == 2, d2["counts"]
    assert d2["counts"]["fixed"] == 2, d2["counts"]
    assert d2["new_debt_score"] < 100 and not d2["clean"]
    assert "New Debt" in to_markdown(d2)
    print("analyze_baseline self-test: OK")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Baseline-aware debt diff (CE-039).")
    p.add_argument(
        "report", nargs="?", help="enhance_repo aggregate or results list JSON."
    )
    p.add_argument("--baseline", help="Baseline snapshot to diff against.")
    p.add_argument(
        "--write-baseline", help="Write a fresh baseline snapshot to this path."
    )
    p.add_argument("--json", action="store_true", help="Emit JSON instead of markdown.")
    p.add_argument(
        "--self-test", action="store_true", help="Run a dependency-free smoke test."
    )
    args = p.parse_args()

    if args.self_test:
        return _self_test()
    if not args.report:
        p.error("report path is required (or use --self-test)")

    with open(args.report) as fh:
        report = json.load(fh)

    if args.write_baseline:
        snap = snapshot(report)
        with open(args.write_baseline, "w") as fh:
            json.dump(snap, fh, indent=2)
        print(
            json.dumps(
                {
                    "written": args.write_baseline,
                    "fingerprints": len(snap["fingerprints"]),
                },
                indent=2,
            )
        )
        return 0

    if args.baseline:
        with open(args.baseline) as fh:
            baseline = json.load(fh)
        result = diff(report, baseline)
        print(json.dumps(result, indent=2) if args.json else to_markdown(result))
        return 0

    # No baseline given → just emit the fingerprint inventory.
    print(json.dumps({"fingerprints": len(extract_units(report))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
