#!/usr/bin/env python3
"""CE-031 — Headless single-repo enhancement driver.

Runs every applicable analysis domain for ONE repository in a single headless command, so a
60-repo batch is one reliable call per repo (no agent-in-the-loop required). Each domain runs as an
isolated subprocess with a per-domain timeout; a domain that crashes or times out is recorded as an
error and never aborts the run (fault isolation). Domains are **language-gated** off
``detect_language`` so Python-only analyzers don't run on a Rust/Go repo. The aggregate JSON is
rewritten after every domain completes, giving live progress for long multi-repo runs.

Usage:
    python enhance_repo.py <repo_path> [--out DIR] [--domains a,b] [--timeout 120] [--json] [--kg]
    python enhance_repo.py --self-test

Output contract (per domain): the analyzer scripts already emit ``{domain, score, grade, findings,
justifications, ...}`` JSON on stdout taking the repo path as argv[1]; this driver aggregates them.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent

# Domain registry. ``langs=None`` → applies to all languages; otherwise the set of primary
# languages the domain is meaningful for (CE-D1 language gating). Only scripts that exist on disk
# are run (CE-D7: no invoking phantom scripts). ``timeout`` is per-domain seconds.
DOMAINS: list[dict[str, Any]] = [
    {"key": "project", "script": "analyze_project.py", "langs": None, "timeout": 90},
    {
        "key": "dependencies",
        "script": "audit_dependencies.py",
        "langs": {"python"},
        "timeout": 120,
    },
    {"key": "codebase", "script": "analyze_codebase.py", "langs": None, "timeout": 180},
    {
        "key": "directory_density",
        "script": "analyze_directory_density.py",
        "langs": None,
        "timeout": 60,
    },
    {"key": "security", "script": "analyze_security.py", "langs": None, "timeout": 120},
    {"key": "env_vars", "script": "scan_env_vars.py", "langs": None, "timeout": 60},
    {
        "key": "documentation",
        "script": "audit_documentation.py",
        "langs": None,
        "timeout": 90,
    },
    {"key": "changelog", "script": "audit_changelog.py", "langs": None, "timeout": 60},
    {"key": "concepts", "script": "trace_concepts.py", "langs": None, "timeout": 90},
    {"key": "ui", "script": "analyze_ui.py", "langs": None, "timeout": 60},
    {"key": "linters", "script": "run_linters.py", "langs": None, "timeout": 180},
    {"key": "tests", "script": "run_tests.py", "langs": None, "timeout": 300},
    {
        "key": "pytest_quality",
        "script": "grade_pytest.py",
        "langs": {"python"},
        "timeout": 90,
    },
    {"key": "skills", "script": "grade_skills.py", "langs": None, "timeout": 60},
    {
        "key": "heuristics",
        "script": "evaluate_heuristics.py",
        "langs": None,
        "timeout": 120,
    },
    {
        "key": "architecture",
        "script": "analyze_architecture.py",
        "langs": None,
        "timeout": 90,
    },
    {
        "key": "version_sync",
        "script": "analyze_version_sync.py",
        "langs": None,
        "timeout": 60,
    },
    # Profiling domains execute the target (import / spawn instances), so they are
    # opt_in: skipped in the default sweep, run only when named via --domains.
    {
        "key": "runtime_profile",
        "script": "analyze_runtime_profile.py",
        "langs": {"python"},
        "timeout": 180,
        "opt_in": True,
    },
    {
        "key": "scale_profile",
        "script": "analyze_scale_profile.py",
        "langs": {"python"},
        "timeout": 180,
        "opt_in": True,
    },
]


def _grade(score: float) -> str:
    return (
        "A"
        if score >= 90
        else "B"
        if score >= 80
        else "C"
        if score >= 70
        else "D"
        if score >= 60
        else "F"
    )


def detect_primary_language(repo: Path) -> str:
    """Run detect_language.py and return the primary language ('python'/'rust'/...)."""
    script = SCRIPTS_DIR / "detect_language.py"
    if not script.exists():
        return "unknown"
    try:
        out = subprocess.run(
            [sys.executable, str(script), str(repo)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        data = json.loads(out.stdout or "{}")
        return str(data.get("primary_language", "unknown"))
    except Exception:
        return "unknown"


def run_domain(domain: dict[str, Any], repo: Path) -> dict[str, Any]:
    """Run one domain script as an isolated subprocess; never raises."""
    script = SCRIPTS_DIR / domain["script"]
    if not script.exists():
        return {"status": "skipped", "reason": "script not found"}
    started = time.monotonic()
    try:
        proc = subprocess.run(
            [sys.executable, str(script), str(repo)],
            capture_output=True,
            text=True,
            timeout=domain["timeout"],
        )
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": f"timeout after {domain['timeout']}s"}
    except Exception as e:  # pragma: no cover - subprocess transport
        return {"status": "error", "error": str(e)}
    elapsed = round(time.monotonic() - started, 1)
    try:
        data = json.loads(proc.stdout or "{}")
    except (json.JSONDecodeError, ValueError):
        return {
            "status": "error",
            "error": "non-JSON output",
            "duration_s": elapsed,
            "stderr": (proc.stderr or "")[-300:],
        }
    return {
        "status": "ok",
        "score": data.get("score"),
        "grade": data.get("grade"),
        "findings": data.get("findings", [])[:25],
        "duration_s": elapsed,
    }


def enhance_repo(
    repo: Path,
    *,
    out_dir: Path | None = None,
    only: set[str] | None = None,
    timeout_override: int | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Run all applicable domains for one repo, writing incrementally. Returns the aggregate."""
    repo = repo.resolve()
    primary = detect_primary_language(repo)
    report: dict[str, Any] = {
        "repo": repo.name,
        "repo_path": str(repo),
        "primary_language": primary,
        "timestamp": now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "domains": {},
    }
    out_file = None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{repo.name}.enhance.json"

    for domain in DOMAINS:
        if only and domain["key"] not in only:
            continue
        # opt_in domains (e.g. profiling, which executes the target) run only when
        # explicitly named via ``only``; never in the default sweep.
        if domain.get("opt_in") and not (only and domain["key"] in only):
            report["domains"][domain["key"]] = {
                "status": "skipped",
                "reason": "opt-in domain; pass --domains to run",
            }
            continue
        if domain["langs"] is not None and primary not in domain["langs"]:
            report["domains"][domain["key"]] = {
                "status": "skipped",
                "reason": f"not applicable to {primary}",
            }
            continue
        d = dict(domain)
        if timeout_override:
            d["timeout"] = timeout_override
        print(f"  [{repo.name}] running {domain['key']}...", file=sys.stderr)
        report["domains"][domain["key"]] = run_domain(d, repo)
        if out_file:  # incremental write → live progress (CE-D6)
            out_file.write_text(json.dumps(report, indent=2))

    scored = [
        v["score"]
        for v in report["domains"].values()
        if v.get("status") == "ok" and isinstance(v.get("score"), (int, float))
    ]
    report["overall_score"] = round(sum(scored) / len(scored), 1) if scored else None
    report["overall_grade"] = _grade(report["overall_score"]) if scored else "N/A"
    report["domains_run"] = len(scored)
    report["domains_errored"] = sum(
        1 for v in report["domains"].values() if v.get("status") == "error"
    )
    if out_file:
        out_file.write_text(json.dumps(report, indent=2))
        report["_out_file"] = str(out_file)
    return report


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Code Enhancement — {report['repo']} ({report['primary_language']})",
        "",
        f"**Overall: {report.get('overall_grade')} ({report.get('overall_score')})** · "
        f"{report.get('domains_run', 0)} domains scored · {report.get('domains_errored', 0)} errored · "
        f"{report['timestamp']}",
        "",
        "| Domain | Grade | Score | Status |",
        "|---|---|---|---|",
    ]
    for key, v in report["domains"].items():
        lines.append(
            f"| {key} | {v.get('grade', '—')} | {v.get('score', '—')} | {v.get('status')}"
            f"{(': ' + v['error']) if v.get('error') else ''} |"
        )
    return "\n".join(lines) + "\n"


def _self_test() -> int:
    """Smoke-test the driver on a tiny synthetic repo (CE-D2). Dependency-free."""
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "fixture"
        repo.mkdir()
        (repo / "main.py").write_text("def add(a, b):\n    return a + b\n")
        (repo / "README.md").write_text("# Fixture\n")
        rep = enhance_repo(
            repo, only={"codebase", "documentation"}, now="2026-01-01T00:00:00Z"
        )
        assert rep["primary_language"] in ("python", "unknown"), rep["primary_language"]
        assert "codebase" in rep["domains"], "codebase domain missing"
        assert "overall_grade" in rep, "no overall grade"
        md = to_markdown(rep)
        assert "Code Enhancement" in md
    print("enhance_repo self-test: OK")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Headless single-repo code-enhancement driver (CE-031)."
    )
    p.add_argument("repo", nargs="?", help="Path to the repository to analyze.")
    p.add_argument("-o", "--out", help="Output directory for the per-repo report.")
    p.add_argument("--domains", help="Comma-separated subset of domain keys to run.")
    p.add_argument("--timeout", type=int, help="Override per-domain timeout (seconds).")
    p.add_argument(
        "--json", action="store_true", help="Print the aggregate JSON to stdout."
    )
    p.add_argument(
        "--markdown", action="store_true", help="Print the markdown report to stdout."
    )
    p.add_argument(
        "--kg",
        action="store_true",
        help="Emit a KG-ingest artifact alongside the report (see kg_ingest_run.py).",
    )
    p.add_argument(
        "--self-test", action="store_true", help="Run a dependency-free smoke test."
    )
    args = p.parse_args()

    if args.self_test:
        return _self_test()
    if not args.repo:
        p.error("repo path is required (or use --self-test)")

    only = {d.strip() for d in args.domains.split(",")} if args.domains else None
    out_dir = Path(args.out).expanduser() if args.out else None
    report = enhance_repo(
        args.repo and Path(args.repo),
        out_dir=out_dir,
        only=only,
        timeout_override=args.timeout,
    )

    if args.kg:
        from kg_ingest_run import build_kg_payload  # local module

        payload = build_kg_payload(report)
        if out_dir:
            (out_dir / f"{report['repo']}.kg.json").write_text(
                json.dumps(payload, indent=2)
            )
        report["_kg_nodes"] = len(payload.get("nodes", []))

    if args.markdown:
        print(to_markdown(report))
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
