#!/usr/bin/env python3
"""False-positive filter for security findings (CE-041).

A two-stage filter that cuts the noise classes a CWE/bandit/pip-audit register is
prone to:

1. **Hard-exclusion rules** — fast, deterministic regex over a finding's
   name+detail+file (DOS/resource-exhaustion advice, rate-limit recommendations,
   resource leaks, open redirects, regex injection, memory-safety findings in
   non-C/C++ files, SSRF in HTML). Always available, no network — fits the
   offline ethos of the code-enhancer analyzers.
2. **LLM confidence re-scoring** *(opt-in, injected)* — when the caller passes a
   ``judge`` callable, each surviving finding is re-scored 1–10 and dropped below
   a threshold (default 8). Safe default: on judge error, **keep** the finding.

The hard-exclusion patterns are ported from Anthropic's
``claude-code-security-review`` (``claudecode/findings_filter.py``, MIT) and
adapted to this skill's finding shape (``{cwe, name, severity, file, detail}``).

CONCEPT:CE-041 — Security false-positive filter
"""

from __future__ import annotations

import re
from typing import Any, Callable

# (compiled pattern, exclusion reason). Ported from claude-code-security-review (MIT).
_RULES: list[tuple[re.Pattern, str]] = [
    (
        re.compile(r"\b(denial of service|dos attack|resource exhaustion)\b", re.I),
        "Generic DOS/resource-exhaustion finding (low signal)",
    ),
    (
        re.compile(r"\b(exhaust|overwhelm|overload).*?(resource|memory|cpu)\b", re.I),
        "Generic DOS/resource-exhaustion finding (low signal)",
    ),
    (
        re.compile(r"\b(infinite|unbounded).*?(loop|recursion)\b", re.I),
        "Generic DOS/resource-exhaustion finding (low signal)",
    ),
    (
        re.compile(r"\b(missing|lack of|no)\s+rate\s+limit", re.I),
        "Generic rate-limiting recommendation",
    ),
    (
        re.compile(r"\b(implement|add)\s+rate\s+limit", re.I),
        "Generic rate-limiting recommendation",
    ),
    (
        re.compile(r"\bunlimited\s+(requests|calls|api)", re.I),
        "Generic rate-limiting recommendation",
    ),
    (
        re.compile(r"\b(resource|memory|file)\s+leak\s+potential", re.I),
        "Resource-management finding (not a security vulnerability)",
    ),
    (
        re.compile(r"\bunclosed\s+(resource|file|connection)", re.I),
        "Resource-management finding (not a security vulnerability)",
    ),
    (
        re.compile(r"\bpotential\s+memory\s+leak", re.I),
        "Resource-management finding (not a security vulnerability)",
    ),
    (
        re.compile(r"\b(open redirect|unvalidated redirect)\b", re.I),
        "Open-redirect finding (not high impact)",
    ),
    (
        re.compile(
            r"\b(regex|regular expression)\s+(injection|denial of service|flooding)\b",
            re.I,
        ),
        "Regex-injection finding (not applicable)",
    ),
]

# Memory-safety patterns are only false-positives *outside* C/C++.
_MEMORY_SAFETY = re.compile(
    r"\b(buffer overflow|stack overflow|heap overflow|use.?after.?free|double.?free|"
    r"null.?pointer.?dereference|out.?of.?bounds?|memory safety|memory corruption|"
    r"segmentation fault|segfault|integer overflow|integer underflow)\b",
    re.I,
)
_SSRF = re.compile(r"\b(ssrf|server.?side.?request.?forgery)\b", re.I)
_C_CPP_EXT = {".c", ".cc", ".cpp", ".h", ".hpp", ".cxx"}


def _finding_text(finding: dict[str, Any]) -> str:
    return f"{finding.get('name', '')} {finding.get('detail', finding.get('description', ''))}".lower()


def _file_ext(finding: dict[str, Any]) -> str:
    path = str(finding.get("file", ""))
    return f".{path.lower().rsplit('.', 1)[-1]}" if "." in path else ""


def hard_exclusion_reason(finding: dict[str, Any]) -> str | None:
    """Return why a finding is a likely false positive, or None to keep it."""
    text = _finding_text(finding)
    ext = _file_ext(finding)

    for pattern, reason in _RULES:
        if pattern.search(text):
            return reason
    # Memory-safety findings are real only in C/C++ sources.
    if ext not in _C_CPP_EXT and _MEMORY_SAFETY.search(text):
        return "Memory-safety finding in non-C/C++ code (not applicable)"
    # SSRF in a static HTML file is not server-side.
    if ext == ".html" and _SSRF.search(text):
        return "SSRF finding in HTML file (not applicable to client-side code)"
    return None


def filter_findings(
    findings: list[dict[str, Any]],
    *,
    use_hard_exclusions: bool = True,
    judge: Callable[[dict[str, Any]], tuple[bool, float, str]] | None = None,
    threshold: float = 8.0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Filter security findings into (kept, excluded, stats).

    ``judge`` is an optional, caller-injected LLM re-scorer returning
    ``(keep, confidence, reason)``; only invoked when supplied (keeping this module
    offline by default). Any judge exception is swallowed and the finding is kept.
    """
    kept: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    breakdown: dict[str, int] = {}

    for finding in findings:
        reason = hard_exclusion_reason(finding) if use_hard_exclusions else None
        if reason:
            excluded.append(
                {**finding, "filter_stage": "hard_rules", "exclusion_reason": reason}
            )
            breakdown[reason] = breakdown.get(reason, 0) + 1
            continue
        if judge is not None:
            try:
                keep, confidence, jreason = judge(finding)
            except Exception:  # noqa: BLE001 — safe default: keep on judge failure
                keep, confidence, jreason = True, 10.0, "judge error; kept"
            if not keep or confidence < threshold:
                excluded.append(
                    {
                        **finding,
                        "filter_stage": "llm",
                        "confidence": confidence,
                        "exclusion_reason": jreason,
                    }
                )
                continue
            kept.append({**finding, "filter_stage": "llm", "confidence": confidence})
        else:
            kept.append({**finding, "filter_stage": "kept"})

    stats = {
        "total": len(findings),
        "kept": len(kept),
        "excluded": len(excluded),
        "exclusion_breakdown": breakdown,
    }
    return kept, excluded, stats


def _self_test() -> int:
    findings = [
        {
            "cwe": "CWE-400",
            "name": "Denial of Service",
            "detail": "resource exhaustion",
            "file": "a.py",
        },
        {
            "cwe": "API",
            "name": "No rate limit on endpoint",
            "detail": "add rate limit",
            "file": "b.py",
        },
        {
            "cwe": "CWE-787",
            "name": "Buffer overflow",
            "detail": "out of bounds write",
            "file": "x.py",
        },
        {
            "cwe": "CWE-787",
            "name": "Buffer overflow",
            "detail": "out of bounds write",
            "file": "x.c",
        },
        {
            "cwe": "CWE-78",
            "name": "OS Command Injection",
            "detail": "shell=True",
            "file": "run.py",
        },
    ]
    kept, excluded, stats = filter_findings(findings)
    # DOS, rate-limit, and non-C buffer-overflow excluded; C buffer-overflow + cmd-injection kept.
    assert stats["excluded"] == 3, stats
    assert {f["cwe"] for f in kept} == {"CWE-787", "CWE-78"}, kept
    assert all(f.get("file", "").endswith((".c", "run.py")) for f in kept), kept

    # LLM stage: a judge that drops low-confidence; and keep-on-error safety.
    def judge(f: dict[str, Any]) -> tuple[bool, float, str]:
        if f["cwe"] == "CWE-78":
            return False, 3.0, "not reachable from untrusted input"
        raise RuntimeError("boom")

    kept2, excluded2, _ = filter_findings(findings, judge=judge)
    assert not any(f["cwe"] == "CWE-78" for f in kept2), "low-confidence not dropped"
    assert any(f["cwe"] == "CWE-787" and f["file"] == "x.c" for f in kept2), (
        "keep-on-error failed"
    )
    print("findings_filter self-test: OK")
    return 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        raise SystemExit(_self_test())
    print(
        "Usage: findings_filter.py --self-test  (this module is imported by analyze_security.py)"
    )
