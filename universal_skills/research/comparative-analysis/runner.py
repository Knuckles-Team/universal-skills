"""Comparative-analysis runner: parallelized analyzer wave + report.

Resolves the analyzer scripts absolutely from this file's location, runs the
full (target x analyze_*.py) job matrix concurrently, runs the cross-source
innovation extraction in the same wave, then barriers and builds the report
arguments programmatically by globbing the produced results JSON.
"""

import argparse
import glob
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
DEFAULT_RESULTS_DIR = SKILL_DIR / "results"
DEFAULT_REPORT = DEFAULT_RESULTS_DIR / "comparative_analysis.md"

# The analyzer wave: (results-suffix index, script). Output contract preserved:
# results/<name>_ca00<i>.json
ANALYZERS = {
    1: "analyze_governance.py",
    2: "analyze_ecosystem_health.py",
    3: "analyze_architecture.py",
    4: "analyze_code_quality.py",
    5: "analyze_security.py",
    6: "analyze_testing.py",
    7: "analyze_documentation.py",
    8: "analyze_performance.py",
}


def _name_for(path: str) -> str:
    return Path(path).resolve().name


def discover_targets() -> list[str]:
    """Fall back to scripts/discover_projects.py when no --target is given."""
    discover = SCRIPTS_DIR / "discover_projects.py"
    if not discover.exists():
        raise SystemExit(
            "No --target given and scripts/discover_projects.py is not present; "
            "pass at least one --target <project-path>."
        )
    proc = subprocess.run(  # noqa: S603
        [sys.executable, str(discover)],
        capture_output=True,
        text=True,
    )
    targets: list[str] = []
    try:
        data = json.loads(proc.stdout)
        for proj in data.get("projects", []):
            if proj.get("exists") and proj.get("path"):
                targets.append(proj["path"])
    except (json.JSONDecodeError, AttributeError):
        pass
    if not targets:
        raise SystemExit(
            "No --target given and discovery produced no existing projects; "
            "pass at least one --target <project-path>."
        )
    return targets


def _run_job(label: str, argv: list[str], out_path: Path) -> dict:
    """Run one analyzer subprocess. Capture failures, never raise."""
    try:
        proc = subprocess.run(  # noqa: S603
            argv,
            capture_output=True,
            text=True,
        )
    except Exception as exc:  # pragma: no cover - subprocess spawn failure
        return {"label": label, "ok": False, "error": type(exc).__name__}
    if proc.returncode != 0:
        return {
            "label": label,
            "ok": False,
            "error": f"exit {proc.returncode}: {proc.stderr.strip()}",
        }
    out_path.write_text(proc.stdout)
    return {"label": label, "ok": True, "out": str(out_path)}


def run_wave(
    targets: list[str],
    sources: list[str],
    results_dir: Path,
    jobs: int,
) -> list[dict]:
    """Run the full (target x analyzer) matrix + innovation extraction concurrently."""
    results_dir.mkdir(parents=True, exist_ok=True)
    plan: list[tuple[str, list[str], Path]] = []

    for target in targets:
        name = _name_for(target)
        for idx, script in ANALYZERS.items():
            label = f"{name}:{script}"
            argv = [sys.executable, str(SCRIPTS_DIR / script), target]
            out_path = results_dir / f"{name}_ca00{idx}.json"
            plan.append((label, argv, out_path))

    # Cross-source innovation extraction runs in the same wave.
    if sources:
        innov_argv = [sys.executable, str(SCRIPTS_DIR / "extract_innovations.py")]
        for src in sources:
            innov_argv += ["--source", src]
        if targets:
            innov_argv += ["--target", targets[0]]
        plan.append(
            (
                "innovation:extract_innovations.py",
                innov_argv,
                results_dir / "innovation_ca009.json",
            )
        )

    outcomes: list[dict] = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {pool.submit(_run_job, *job): job[0] for job in plan}
        for fut in as_completed(futures):
            outcome = fut.result()
            outcomes.append(outcome)
            status = "OK " if outcome["ok"] else "FAIL"
            print(f"[{status}] {outcome['label']}", file=sys.stderr)
            if not outcome["ok"]:
                print(f"        {outcome['error']}", file=sys.stderr)
    return outcomes


def run_report(results_dir: Path, report: Path) -> int:
    """Barrier-stage: glob produced JSON and generate the report once."""
    result_files = sorted(glob.glob(str(results_dir / "*_ca00*.json")))
    result_files += sorted(glob.glob(str(results_dir / "*innov*.json")))
    # De-dup while preserving order.
    ordered = list(dict.fromkeys(result_files))
    if not ordered:
        print("No result JSON produced; skipping report.", file=sys.stderr)
        return 1

    report.parent.mkdir(parents=True, exist_ok=True)
    argv = (
        [sys.executable, str(SCRIPTS_DIR / "generate_comparison_report.py")]
        + ordered
        + ["--output", str(report)]
    )
    proc = subprocess.run(argv)  # noqa: S603
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the comparative-analysis analyzer wave in parallel, then report."
    )
    parser.add_argument(
        "--target",
        action="append",
        default=[],
        help="Project path to analyze (repeatable). Falls back to discover_projects.py.",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Paper/repo to compare against for innovation extraction (repeatable).",
    )
    parser.add_argument(
        "--results-dir",
        default=str(DEFAULT_RESULTS_DIR),
        help="Directory for per-analyzer result JSON (default: the skill's results/).",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT),
        help="Output path for the generated comparison report.",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=min(8, os.cpu_count() or 4),
        help="Max concurrent analyzer subprocesses.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the wave against this skill's own directory as a smoke test.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        args.target = args.target or [str(SKILL_DIR)]
        if args.results_dir == str(DEFAULT_RESULTS_DIR):
            args.results_dir = str(SKILL_DIR / ".self_test_results")
        if args.report == str(DEFAULT_REPORT):
            args.report = str(Path(args.results_dir) / "comparative_analysis.md")

    targets = args.target or discover_targets()
    results_dir = Path(args.results_dir).resolve()
    report = Path(args.report).resolve()

    print(
        f"Targets: {', '.join(targets)} | sources: {len(args.source)} | jobs: {args.jobs}",
        file=sys.stderr,
    )
    outcomes = run_wave(targets, args.source, results_dir, args.jobs)
    failures = [o for o in outcomes if not o["ok"]]

    rc = run_report(results_dir, report)
    if rc == 0:
        print(f"Report written to {report}", file=sys.stderr)

    if failures:
        print(f"{len(failures)} analyzer job(s) failed.", file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
