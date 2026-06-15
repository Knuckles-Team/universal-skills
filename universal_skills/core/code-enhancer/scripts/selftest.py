#!/usr/bin/env python3
"""CE-033 — Toolchain self-test harness.

Smoke-validates the whole code-enhancer toolchain before a 60-repo batch (CE-D2: previously 0/25
scripts could be smoke-tested). For each analyzer script it either calls ``--self-test`` (if the
script supports it) or runs it against a tiny synthetic fixture repo and asserts it exits 0 and
emits parseable JSON. Reports a per-script pass/fail matrix and a non-zero exit if anything broke,
so this can gate a batch run in CI.

Usage:
    python selftest.py [--json]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

# Scripts that take a repo path as argv[1] and emit JSON (the analyzers). Orchestrators/report
# generators are validated via their own --self-test or skipped here.
ANALYZER_SCRIPTS = [
    "detect_language.py",
    "analyze_project.py",
    "analyze_codebase.py",
    "analyze_directory_density.py",
    "analyze_security.py",
    "analyze_minimalism.py",
    "scan_env_vars.py",
    "audit_documentation.py",
    "audit_changelog.py",
    "trace_concepts.py",
    "analyze_ui.py",
    "run_linters.py",
    "grade_pytest.py",
    "grade_skills.py",
    "evaluate_heuristics.py",
    "analyze_architecture.py",
    "analyze_version_sync.py",
    "analyze_opportunities.py",
    "analyze_runtime_profile.py",
    "analyze_scale_profile.py",
]
# Scripts that expose their own --self-test.
SELFTEST_SCRIPTS = [
    "enhance_repo.py",
    "kg_ingest_run.py",
    "kg_query_runs.py",
    "analyze_baseline.py",
    "findings_filter.py",
    "apply_dependency_updates.py",
    "analyze_dependency_migration.py",
]


def _make_fixture(root: Path) -> Path:
    repo = root / "fixture"
    repo.mkdir()
    (repo / "main.py").write_text(
        "import os\n\n\ndef add(a, b):\n    '''Add two numbers.'''\n    return a + b\n"
    )
    (repo / "README.md").write_text("# Fixture\n\nA tiny repo.\n")
    (repo / "pyproject.toml").write_text(
        '[project]\nname = "fixture"\nversion = "0.1.0"\n'
    )
    (repo / "CHANGELOG.md").write_text("# Changelog\n\n## [0.1.0]\n")
    return repo


def run_selftest() -> dict[str, dict]:
    results: dict[str, dict] = {}
    with tempfile.TemporaryDirectory() as td:
        repo = _make_fixture(Path(td))
        for name in SELFTEST_SCRIPTS:
            script = SCRIPTS_DIR / name
            if not script.exists():
                results[name] = {"status": "missing"}
                continue
            try:
                proc = subprocess.run(
                    [sys.executable, str(script), "--self-test"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                results[name] = {
                    "status": "pass" if proc.returncode == 0 else "fail",
                    "detail": (proc.stderr or proc.stdout or "")[-160:]
                    if proc.returncode
                    else "",
                }
            except Exception as e:  # noqa: BLE001
                results[name] = {"status": "fail", "detail": str(e)}

        for name in ANALYZER_SCRIPTS:
            script = SCRIPTS_DIR / name
            if not script.exists():
                results[name] = {"status": "missing"}
                continue
            try:
                proc = subprocess.run(
                    [sys.executable, str(script), str(repo)],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if proc.returncode != 0:
                    results[name] = {
                        "status": "fail",
                        "detail": (proc.stderr or "")[-160:],
                    }
                    continue
                json.loads(proc.stdout or "{}")  # must be parseable
                results[name] = {"status": "pass"}
            except json.JSONDecodeError:
                results[name] = {"status": "fail", "detail": "non-JSON output"}
            except Exception as e:  # noqa: BLE001
                results[name] = {"status": "fail", "detail": str(e)}
    return results


def main() -> int:
    p = argparse.ArgumentParser(
        description="Code-enhancer toolchain self-test (CE-033)."
    )
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    results = run_selftest()
    passed = sum(1 for v in results.values() if v["status"] == "pass")
    failed = [k for k, v in results.items() if v["status"] == "fail"]
    missing = [k for k, v in results.items() if v["status"] == "missing"]

    if args.json:
        print(
            json.dumps(
                {
                    "results": results,
                    "passed": passed,
                    "failed": failed,
                    "missing": missing,
                },
                indent=2,
            )
        )
    else:
        for name, v in sorted(results.items()):
            mark = {"pass": "✓", "fail": "✗", "missing": "?"}.get(v["status"], "?")
            line = f"  {mark} {name}"
            if v.get("detail"):
                line += f"  — {v['detail']}"
            print(line)
        print(
            f"\n{passed} passed, {len(failed)} failed, {len(missing)} missing "
            f"of {len(results)} scripts"
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
