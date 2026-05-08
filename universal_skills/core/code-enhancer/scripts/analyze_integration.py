#!/usr/bin/env python3
"""CE-021: Cross-project integration analysis for code-enhancer skill.

Analyzes inter-project dependencies, version alignment, import tracing,
and circular dependency detection across multiple projects.

CONCEPT:CE-021 — Cross-Project Integration
"""

import json
import re
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

_SKIP_DIRS = frozenset(
    {
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".git",
        "build",
        "dist",
        ".tox",
    }
)


def _parse_pyproject_deps(path: Path) -> dict:
    """Parse pyproject.toml for project name and dependencies."""
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return {"name": path.parent.name, "deps": {}, "extras": {}}

    project = data.get("project", {})
    name = project.get("name", path.parent.name)

    deps: dict[str, str] = {}
    for d in project.get("dependencies", []):
        pkg, version = _split_dep(d)
        if pkg:
            deps[pkg] = version

    extras: dict[str, dict[str, str]] = {}
    for group, group_deps in project.get("optional-dependencies", {}).items():
        extras[group] = {}
        for d in group_deps:
            pkg, version = _split_dep(d)
            if pkg:
                extras[group][pkg] = version

    return {"name": name, "deps": deps, "extras": extras}


def _split_dep(dep_str: str) -> tuple[str, str]:
    """Split a dependency string into (name, version_spec)."""
    dep_str = dep_str.strip()
    # Handle extras like package[extra]>=1.0
    match = re.match(r"([a-zA-Z0-9_-]+)(?:\[.*?\])?\s*(.*)", dep_str)
    if match:
        name = match.group(1).lower().replace("-", "_")
        version = match.group(2).strip()
        return name, version
    return "", ""


def _parse_package_json_deps(path: Path) -> dict:
    """Parse package.json for project name and dependencies."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"name": path.parent.name, "deps": {}}

    name = data.get("name", path.parent.name)
    deps: dict[str, str] = {}
    for section in ("dependencies", "devDependencies", "peerDependencies"):
        for pkg, version in data.get(section, {}).items():
            deps[pkg] = version

    return {"name": name, "deps": deps}


def _scan_imports(root: Path, project_name: str) -> set[str]:
    """Scan Python files for import statements, returning imported packages."""
    imports: set[str] = set()
    for f in root.rglob("*.py"):
        if any(skip in f.parts for skip in _SKIP_DIRS):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for match in re.finditer(
            r"(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_]*)", content
        ):
            pkg = match.group(1).lower().replace("-", "_")
            if pkg != project_name.lower().replace("-", "_"):
                imports.add(pkg)
    return imports


def _detect_version_conflicts(projects: list[dict]) -> list[dict]:
    """Detect version specification conflicts across projects."""
    conflicts: list[dict] = []
    # Build package → [(project, version_spec)] mapping
    pkg_versions: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for proj in projects:
        for pkg, version in proj["deps"].items():
            if version:
                pkg_versions[pkg].append((proj["name"], version))

    # Check for conflicts (simplified: major version disagreement)
    for pkg, consumers in pkg_versions.items():
        if len(consumers) < 2:
            continue
        # Extract major versions
        majors: set[str] = set()
        for _, ver_spec in consumers:
            major_match = re.search(r"(\d+)\.", ver_spec)
            if major_match:
                majors.add(major_match.group(1))

        if len(majors) > 1:
            conflicts.append(
                {
                    "package": pkg,
                    "consumers": [{"project": p, "version": v} for p, v in consumers],
                    "major_versions": sorted(majors),
                }
            )

    return conflicts


def _detect_circular_deps(dep_graph: dict[str, set[str]]) -> list[list[str]]:
    """Detect circular dependencies using DFS."""
    cycles: list[list[str]] = []
    visited: set[str] = set()
    rec_stack: set[str] = set()

    def dfs(node: str, path: list[str]) -> None:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in dep_graph.get(node, set()):
            if neighbor not in visited:
                dfs(neighbor, path)
            elif neighbor in rec_stack:
                # Found cycle — extract it
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        path.pop()
        rec_stack.discard(node)

    for node in dep_graph:
        if node not in visited:
            dfs(node, [])

    return cycles


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def analyze_integration(project_dirs: list[str]) -> dict:
    """Analyze cross-project integration and dependencies.

    Args:
        project_dirs: List of paths to project root directories.

    Returns:
        dict with domain, score, grade, findings, dependency graph, conflicts.
    """
    if len(project_dirs) < 2:
        return {
            "domain": "Cross-Project Integration",
            "score": -1,
            "grade": "N/A",
            "findings": ["Need at least 2 projects for integration analysis"],
            "justifications": [],
            "dependency_graph": {},
            "conflicts": [],
            "circular_deps": [],
        }

    # Parse all projects
    projects: list[dict] = []
    project_names: set[str] = set()

    for dir_path in project_dirs:
        root = Path(dir_path).resolve()
        pyproject = root / "pyproject.toml"
        pkg_json = root / "package.json"

        if pyproject.exists():
            proj = _parse_pyproject_deps(pyproject)
            proj["path"] = str(root)
            proj["language"] = "python"
            projects.append(proj)
            project_names.add(proj["name"].lower().replace("-", "_"))
        elif pkg_json.exists():
            proj = _parse_package_json_deps(pkg_json)
            proj["path"] = str(root)
            proj["language"] = "node"
            projects.append(proj)
            project_names.add(proj["name"])

    if not projects:
        return {
            "domain": "Cross-Project Integration",
            "score": -1,
            "grade": "N/A",
            "findings": ["No parseable projects found"],
            "justifications": [],
            "dependency_graph": {},
            "conflicts": [],
            "circular_deps": [],
        }

    # Build inter-project dependency graph
    dep_graph: dict[str, set[str]] = {}
    for proj in projects:
        proj_key = proj["name"].lower().replace("-", "_")
        internal_deps: set[str] = set()
        for dep_name in proj["deps"]:
            dep_normalized = dep_name.lower().replace("-", "_")
            if dep_normalized in project_names and dep_normalized != proj_key:
                internal_deps.add(dep_normalized)
        dep_graph[proj_key] = internal_deps

    # Detect version conflicts
    conflicts = _detect_version_conflicts(projects)

    # Detect circular dependencies
    circular = _detect_circular_deps(dep_graph)

    # Detect unused declared dependencies (declared but not imported)
    unused_deps: list[dict] = []
    for proj in projects:
        if proj["language"] != "python":
            continue
        root = Path(proj["path"])
        imports = _scan_imports(root, proj["name"])
        for dep_name in proj["deps"]:
            dep_norm = dep_name.lower().replace("-", "_")
            # Skip self-references and common infra deps
            if dep_norm in project_names and dep_norm not in imports:
                # Check if it's used via extras
                found_in_extras = False
                for extra_deps in proj.get("extras", {}).values():
                    if dep_name in extra_deps:
                        found_in_extras = True
                        break
                if not found_in_extras and dep_norm in project_names:
                    unused_deps.append(
                        {
                            "project": proj["name"],
                            "declared_dep": dep_name,
                        }
                    )

    # Scoring
    score = 100
    findings: list[str] = []

    if conflicts:
        penalty = min(25, len(conflicts) * 5)
        score -= penalty
        for c in conflicts[:5]:
            findings.append(
                f"Version conflict on '{c['package']}': "
                + ", ".join(f"{x['project']}→{x['version']}" for x in c["consumers"])
            )

    if circular:
        score -= 15
        for cycle in circular[:3]:
            findings.append(f"Circular dependency: {' → '.join(cycle)}")

    if unused_deps:
        penalty = min(15, len(unused_deps) * 3)
        score -= penalty
        for ud in unused_deps[:5]:
            findings.append(
                f"Unused internal dep: {ud['project']} declares '{ud['declared_dep']}' "
                f"but does not import it"
            )

    # Integration health
    connected_projects = sum(1 for deps in dep_graph.values() if deps)
    if connected_projects == 0 and len(projects) > 1:
        findings.append(
            "No inter-project dependencies detected — projects may be siloed"
        )

    score = max(0, score)

    metrics = {
        "projects_analyzed": len(projects),
        "internal_dependencies": sum(len(d) for d in dep_graph.values()),
        "version_conflicts": len(conflicts),
        "circular_dependencies": len(circular),
        "unused_internal_deps": len(unused_deps),
        "connected_projects": connected_projects,
    }

    justifications = [
        {
            "criterion": "integration_cohesiveness",
            "points": score,
            "evidence": json.dumps(metrics),
            "reasoning": (
                f"Analyzed {len(projects)} projects. "
                f"{metrics['internal_dependencies']} inter-project deps, "
                f"{len(conflicts)} version conflicts, "
                f"{len(circular)} circular deps."
            ),
        }
    ]

    return {
        "domain": "Cross-Project Integration",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": justifications,
        "dependency_graph": {k: sorted(v) for k, v in dep_graph.items()},
        "conflicts": conflicts,
        "circular_deps": circular,
        "unused_deps": unused_deps[:10],
        "metrics": metrics,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: analyze_integration.py <dir1> <dir2> [dir3 ...]")
        sys.exit(1)
    print(json.dumps(analyze_integration(sys.argv[1:]), indent=2))
