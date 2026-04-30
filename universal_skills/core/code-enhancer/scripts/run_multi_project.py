#!/usr/bin/env python3
"""CE-020: Multi-project orchestration for code-enhancer skill.

Runs code-enhancer analysis across multiple projects in parallel using
asyncio with configurable concurrency. Produces per-project reports and
a unified cross-project summary.

CONCEPT:CE-020 — Multi-Project Orchestration
"""

import asyncio
import json
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path


def _discover_projects(pattern: str) -> list[str]:
    """Discover project directories matching a glob pattern.

    Supports:
        - Direct paths: "/home/apps/workspace/agent-packages/agent-utilities"
        - Glob patterns: "agent-packages/agents/*"
        - Comma-separated: "agent-packages/agents/*,agent-packages/skills/*"
    """
    projects: list[str] = []
    for p in pattern.split(","):
        p = p.strip()
        path = Path(p)
        if path.is_dir():
            # Direct directory
            if (path / "pyproject.toml").exists() or (path / "package.json").exists():
                projects.append(str(path.resolve()))
            else:
                # Maybe a parent — scan children
                for child in sorted(path.iterdir()):
                    if child.is_dir() and (
                        (child / "pyproject.toml").exists()
                        or (child / "package.json").exists()
                    ):
                        projects.append(str(child.resolve()))
        else:
            # Glob pattern
            for match in sorted(Path(".").glob(p)):
                if match.is_dir() and (
                    (match / "pyproject.toml").exists()
                    or (match / "package.json").exists()
                ):
                    projects.append(str(match.resolve()))

    return sorted(set(projects))


def _run_single_project(project_dir: str) -> dict:
    """Run all analysis scripts on a single project. Synchronous.

    Returns a dict with project name and all domain results.
    """
    from pathlib import Path as _P

    root = _P(project_dir)
    project_name = root.name
    results: list[dict] = []
    timing: dict[str, float] = {}

    # Import and run each analyzer
    scripts_dir = _P(__file__).parent

    analyzers = [
        ("analyze_project", "analyze_project"),
        ("audit_dependencies", "audit_dependencies"),
        ("analyze_codebase", "analyze_codebase"),
        ("analyze_security", "analyze_security"),
        ("analyze_tests", "analyze_tests"),
        ("audit_documentation", "audit_documentation"),
        ("analyze_architecture", "analyze_architecture"),
        ("trace_concepts", "trace_concepts"),
        ("run_linters", "run_linters"),
        ("run_precommit", "run_precommit"),
        ("run_tests", "run_tests"),
        ("analyze_directory_density", "analyze_directory_density"),
        ("analyze_ui", "analyze_ui"),
        ("analyze_version_sync", "analyze_version_sync"),
        ("audit_changelog", "audit_changelog"),
        ("grade_pytest", "grade_pytest"),
        ("scan_env_vars", "scan_env_vars"),
    ]

    for module_name, func_name in analyzers:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                module_name, str(scripts_dir / f"{module_name}.py")
            )
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            func = getattr(mod, func_name)

            start = time.monotonic()
            result = func(project_dir)
            elapsed = time.monotonic() - start
            timing[module_name] = round(elapsed, 2)

            # Skip N/A results (score == -1)
            if result.get("score", 0) != -1:
                results.append(result)
        except Exception as e:
            results.append({
                "domain": module_name,
                "score": 0,
                "grade": "F",
                "findings": [f"Analysis error: {str(e)[:200]}"],
                "justifications": [],
            })

    # Compute GPA
    scored = [r for r in results if r.get("score", -1) >= 0]
    grade_points = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}
    gpa = 0.0
    if scored:
        gpa = sum(grade_points.get(r.get("grade", "F"), 0.0) for r in scored) / len(scored)

    return {
        "project": project_name,
        "path": project_dir,
        "domain_results": results,
        "gpa": round(gpa, 2),
        "domain_count": len(results),
        "timing": timing,
    }


async def _run_project_async(project_dir: str, executor: ProcessPoolExecutor,
                              semaphore: asyncio.Semaphore) -> dict:
    """Run analysis on a project with concurrency control."""
    async with semaphore:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, _run_single_project, project_dir)


async def run_multi_project(
    project_dirs: list[str],
    concurrency: int = 4,
    output_dir: str | None = None,
) -> dict:
    """Run code-enhancer on multiple projects in parallel.

    Args:
        project_dirs: List of project root paths.
        concurrency: Max concurrent analyses (default 4).
        output_dir: Optional root for per-project reports.

    Returns:
        dict with per-project results, unified summary, and integration analysis.
    """
    semaphore = asyncio.Semaphore(concurrency)
    start_time = time.monotonic()

    with ProcessPoolExecutor(max_workers=concurrency) as executor:
        tasks = [
            _run_project_async(d, executor, semaphore)
            for d in project_dirs
        ]
        project_results = await asyncio.gather(*tasks, return_exceptions=True)

    elapsed = time.monotonic() - start_time

    # Process results
    successful: list[dict] = []
    errors: list[dict] = []
    for i, result in enumerate(project_results):
        if isinstance(result, Exception):
            errors.append({
                "project": project_dirs[i],
                "error": str(result),
            })
        else:
            successful.append(result)

    # Build cross-project comparison table
    comparison: list[dict] = []
    for proj in successful:
        row = {"project": proj["project"], "gpa": proj["gpa"]}
        for dr in proj["domain_results"]:
            domain_key = dr["domain"].lower().replace(" ", "_").replace("&", "and")
            row[domain_key] = dr.get("grade", "N/A")
        comparison.append(row)

    # Sort by GPA ascending (worst first)
    comparison.sort(key=lambda x: x.get("gpa", 0))

    # Run integration analysis if multiple successful projects
    integration_result = {}
    if len(successful) >= 2:
        try:
            from analyze_integration import analyze_integration
            integration_result = analyze_integration(
                [p["path"] for p in successful]
            )
        except ImportError:
            # Try relative import
            try:
                scripts_dir = Path(__file__).parent
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "analyze_integration",
                    str(scripts_dir / "analyze_integration.py"),
                )
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    integration_result = mod.analyze_integration(
                        [p["path"] for p in successful]
                    )
            except Exception as e:
                integration_result = {"error": str(e)}

    # Write per-project reports and SDD handoffs to each project's own .specify/
    if output_dir:
        out_root = Path(output_dir)
        for proj in successful:
            proj_report_dir = out_root / proj["project"]
            proj_report_dir.mkdir(parents=True, exist_ok=True)
            (proj_report_dir / "results.json").write_text(
                json.dumps(proj, indent=2), encoding="utf-8"
            )

            # Write SDD handoff to each project's own .specify/ folder
            proj_path = Path(proj["path"])
            if proj_path.is_dir():
                try:
                    scripts_dir = Path(__file__).parent
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "generate_sdd_handoff",
                        str(scripts_dir / "generate_sdd_handoff.py"),
                    )
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        mod.generate_sdd_handoff(
                            proj["domain_results"],
                            project_name=proj["project"],
                            output_dir=str(proj_path),  # per-project .specify/
                        )
                except Exception:
                    pass  # SDD handoff is best-effort

        # Write unified summary
        summary_path = out_root / "summary.json"
        summary_path.write_text(json.dumps({
            "comparison": comparison,
            "integration": integration_result,
            "metadata": {
                "projects_analyzed": len(successful),
                "errors": len(errors),
                "elapsed_seconds": round(elapsed, 1),
                "concurrency": concurrency,
            },
        }, indent=2), encoding="utf-8")

    return {
        "project_results": successful,
        "comparison": comparison,
        "integration": integration_result,
        "errors": errors,
        "metadata": {
            "projects_analyzed": len(successful),
            "errors": len(errors),
            "elapsed_seconds": round(elapsed, 1),
            "concurrency": concurrency,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


def run_multi_project_sync(
    project_pattern: str,
    concurrency: int = 4,
    output_dir: str | None = None,
) -> dict:
    """Synchronous wrapper for multi-project analysis.

    Args:
        project_pattern: Glob pattern or comma-separated paths.
        concurrency: Max parallel projects.
        output_dir: Optional output directory.
    """
    project_dirs = _discover_projects(project_pattern)
    if not project_dirs:
        return {"error": f"No projects found matching: {project_pattern}"}

    return asyncio.run(run_multi_project(project_dirs, concurrency, output_dir))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Run code-enhancer across multiple projects"
    )
    parser.add_argument("pattern", help="Project glob pattern or comma-separated dirs")
    parser.add_argument("-c", "--concurrency", type=int, default=4,
                        help="Max parallel projects (default: 4)")
    parser.add_argument("-o", "--output", help="Output directory for reports")
    args = parser.parse_args()

    result = run_multi_project_sync(args.pattern, args.concurrency, args.output)
    print(json.dumps(result, indent=2))
