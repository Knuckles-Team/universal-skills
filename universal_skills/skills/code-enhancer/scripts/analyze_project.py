#!/usr/bin/env python3
"""FR-001: Project analysis for code-enhancer skill.

Scans a target repository for architectural patterns, ecosystem markers,
and development experience indicators. Produces a 0-100 score with
per-criterion justifications.

CONCEPT:CE-001 — Project Structure Analysis
"""

import json
import sys
import tomllib
from pathlib import Path

# ---------------------------------------------------------------------------
# Scoring criteria — each worth up to 10 points, 10 criteria = 100 max
# ---------------------------------------------------------------------------
CRITERIA = [
    "has_pyproject",
    "project_type_detected",
    "externalized_prompts",
    "observability",
    "testing_suite",
    "agents_md",
    "pre_commit_hooks",
    "gitignore",
    "env_template",
    "protocol_support",
]

ECOSYSTEM_MARKERS = {
    "pydantic-ai": "Pydantic-AI Agent",
    "pydantic-ai-slim": "Pydantic-AI Agent",
    "pydantic-graph": "Graph Agent",
    "fastmcp": "MCP Server",
    "fastapi": "Web Agent / API",
    "agent-utilities": "Agent-Utilities Ecosystem",
}


def _parse_deps_from_pyproject(path: Path) -> list[str]:
    """Parse dependency names from pyproject.toml using tomllib."""
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        deps: list[str] = []
        # [project].dependencies
        for d in data.get("project", {}).get("dependencies", []):
            name = (
                d.split("[")[0]
                .split("<")[0]
                .split(">")[0]
                .split("=")[0]
                .split("~")[0]
                .split("!")[0]
                .strip()
            )
            if name:
                deps.append(name.lower())
        # [project.optional-dependencies]
        for group_deps in (
            data.get("project", {}).get("optional-dependencies", {}).values()
        ):
            for d in group_deps:
                name = (
                    d.split("[")[0]
                    .split("<")[0]
                    .split(">")[0]
                    .split("=")[0]
                    .split("~")[0]
                    .split("!")[0]
                    .strip()
                )
                if name:
                    deps.append(name.lower())
        return deps
    except Exception:
        return []


def _parse_deps_from_requirements(path: Path) -> list[str]:
    """Parse dependency names from requirements.txt."""
    deps: list[str] = []
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                name = (
                    line.split("[")[0]
                    .split("<")[0]
                    .split(">")[0]
                    .split("=")[0]
                    .split("~")[0]
                    .split("!")[0]
                    .strip()
                )
                if name:
                    deps.append(name.lower())
    except Exception:
        pass
    return deps


def analyze_project(root_dir: str = ".") -> dict:
    """Analyze project structure and return scored results.

    Returns:
        dict with keys: score, grade, findings, justifications, details
    """
    root = Path(root_dir).resolve()
    findings: list[str] = []
    justifications: list[dict] = []
    score = 0
    details: dict = {}

    # --- Criterion 1: has_pyproject (10 pts) ---
    pyproject_path = root / "pyproject.toml"
    requirements_path = root / "requirements.txt"
    deps: list[str] = []

    criterion_score = 0
    has_pyproject = pyproject_path.exists()
    has_requirements = requirements_path.exists()

    if has_pyproject:
        deps.extend(_parse_deps_from_pyproject(pyproject_path))
        criterion_score += 5
        details["has_pyproject"] = True

    if has_requirements:
        deps.extend(_parse_deps_from_requirements(requirements_path))
        criterion_score += 5
        details["has_requirements"] = True

    score += criterion_score
    details["dep_count"] = len(set(deps))

    if has_pyproject and has_requirements:
        justifications.append(
            {
                "criterion": "has_pyproject",
                "points": 10,
                "evidence": "pyproject.toml and requirements.txt",
                "reasoning": "Both pyproject.toml and requirements.txt exist, fulfilling mandatory Python project requirements",
            }
        )
    elif has_pyproject:
        justifications.append(
            {
                "criterion": "has_pyproject",
                "points": 5,
                "evidence": str(pyproject_path),
                "reasoning": "pyproject.toml found, but requirements.txt is missing (mandatory to build python packages)",
            }
        )
    elif has_requirements:
        justifications.append(
            {
                "criterion": "has_pyproject",
                "points": 5,
                "evidence": str(requirements_path),
                "reasoning": "requirements.txt found, but pyproject.toml is missing",
            }
        )
    else:
        justifications.append(
            {
                "criterion": "has_pyproject",
                "points": 0,
                "evidence": str(root),
                "reasoning": "No pyproject.toml or requirements.txt found",
            }
        )

    # --- Criterion 2: project_type_detected (10 pts) ---
    detected_types: list[str] = []
    for marker, p_type in ECOSYSTEM_MARKERS.items():
        if any(marker in d for d in deps):
            detected_types.append(p_type)
            findings.append(f"Detected ecosystem marker: {marker} → {p_type}")

    if detected_types:
        score += 10
        details["project_types"] = detected_types
        justifications.append(
            {
                "criterion": "project_type_detected",
                "points": 10,
                "evidence": ", ".join(detected_types),
                "reasoning": f"Identified {len(detected_types)} ecosystem marker(s) in dependencies",
            }
        )
    else:
        justifications.append(
            {
                "criterion": "project_type_detected",
                "points": 0,
                "evidence": "dependency list",
                "reasoning": "No recognized ecosystem markers found in dependencies",
            }
        )

    # --- Criterion 3: externalized_prompts (10 pts) ---
    prompt_dirs = [
        root / "prompts",
        root / "agent_utilities" / "prompts",
    ]
    # Also check any <pkg_name>/prompts/ pattern
    for child in root.iterdir():
        if child.is_dir() and (child / "prompts").is_dir():
            prompt_dirs.append(child / "prompts")

    has_prompts = any(d.is_dir() for d in prompt_dirs)
    if has_prompts:
        prompt_dir = next(d for d in prompt_dirs if d.is_dir())
        prompt_count = len(list(prompt_dir.glob("*")))
        score += 10
        findings.append(
            f"Externalized prompts directory found with {prompt_count} files"
        )
        justifications.append(
            {
                "criterion": "externalized_prompts",
                "points": 10,
                "evidence": str(prompt_dir),
                "reasoning": f"Prompts directory contains {prompt_count} externalized prompt files",
            }
        )
    else:
        justifications.append(
            {
                "criterion": "externalized_prompts",
                "points": 0,
                "evidence": str(root),
                "reasoning": "No prompts/ directory found. Prompts may be hardcoded in source.",
            }
        )

    # --- Criterion 4: observability (10 pts) ---
    obs_markers = [
        "logfire",
        "pydantic-ai-slim[logfire]",
        "sentry-sdk",
        "opentelemetry",
    ]
    found_obs = [m for m in obs_markers if any(m in d for d in deps)]
    if found_obs:
        score += 10
        findings.append(f"Observability integration: {', '.join(found_obs)}")
        justifications.append(
            {
                "criterion": "observability",
                "points": 10,
                "evidence": ", ".join(found_obs),
                "reasoning": "Observability/telemetry dependencies detected",
            }
        )
    else:
        justifications.append(
            {
                "criterion": "observability",
                "points": 0,
                "evidence": "dependency list",
                "reasoning": "No observability tools (logfire, sentry, opentelemetry) found",
            }
        )

    # --- Criterion 5: testing_suite (10 pts) ---
    has_tests = (root / "tests").is_dir() or (root / "test").is_dir()
    has_pytest = "pytest" in deps
    test_score = 0
    if has_tests:
        test_score += 5
    if has_pytest:
        test_score += 5
    score += test_score
    justifications.append(
        {
            "criterion": "testing_suite",
            "points": test_score,
            "evidence": f"tests dir: {has_tests}, pytest dep: {has_pytest}",
            "reasoning": f"{'Tests directory exists' if has_tests else 'No tests directory'}, "
            f"{'pytest in dependencies' if has_pytest else 'pytest not in dependencies'}",
        }
    )

    # --- Criterion 6: agents_md (10 pts) ---
    agents_md = root / "AGENTS.md"
    if agents_md.exists():
        size = agents_md.stat().st_size
        points = 10 if size > 500 else 5
        score += points
        justifications.append(
            {
                "criterion": "agents_md",
                "points": points,
                "evidence": f"{agents_md} ({size} bytes)",
                "reasoning": f"AGENTS.md exists with {'comprehensive' if size > 500 else 'minimal'} content",
            }
        )
    else:
        justifications.append(
            {
                "criterion": "agents_md",
                "points": 0,
                "evidence": str(root),
                "reasoning": "No AGENTS.md found — missing agentic project documentation",
            }
        )

    # --- Criterion 7: pre_commit_hooks (10 pts) ---
    precommit = root / ".pre-commit-config.yaml"
    if precommit.exists():
        score += 10
        justifications.append(
            {
                "criterion": "pre_commit_hooks",
                "points": 10,
                "evidence": str(precommit),
                "reasoning": "Pre-commit configuration found for automated code quality checks",
            }
        )
    else:
        justifications.append(
            {
                "criterion": "pre_commit_hooks",
                "points": 0,
                "evidence": str(root),
                "reasoning": "No .pre-commit-config.yaml — no automated linting on commit",
            }
        )

    # --- Criterion 8: gitignore (10 pts) ---
    gitignore = root / ".gitignore"
    if gitignore.exists():
        score += 10
        justifications.append(
            {
                "criterion": "gitignore",
                "points": 10,
                "evidence": str(gitignore),
                "reasoning": ".gitignore exists to prevent committing build artifacts and secrets",
            }
        )
    else:
        justifications.append(
            {
                "criterion": "gitignore",
                "points": 0,
                "evidence": str(root),
                "reasoning": "No .gitignore — risk of committing sensitive or generated files",
            }
        )

    # --- Criterion 9: env_template (10 pts) ---
    env_templates = [
        root / ".env.example",
        root / ".env.template",
        root / ".env.sample",
    ]
    has_env = any(f.exists() for f in env_templates)
    if has_env:
        score += 10
        found = next(f for f in env_templates if f.exists())
        justifications.append(
            {
                "criterion": "env_template",
                "points": 10,
                "evidence": str(found),
                "reasoning": "Environment template exists for onboarding and secret management",
            }
        )
    else:
        justifications.append(
            {
                "criterion": "env_template",
                "points": 0,
                "evidence": str(root),
                "reasoning": "No .env.example or .env.template — may hinder developer onboarding",
            }
        )

    # --- Criterion 10: protocol_support (10 pts) ---
    protocol_indicators = {
        "A2A": (root / "a2a.py").exists() or "a2a" in " ".join(deps),
        "ACP": "pydantic-acp" in " ".join(deps),
        "MCP": any(
            f.name.endswith("_mcp.py") or "mcp_server" in f.name
            for f in root.rglob("*.py")
            if f.is_file()
        ),
    }
    found_protocols = [k for k, v in protocol_indicators.items() if v]
    if found_protocols:
        points = min(10, len(found_protocols) * 4)
        score += points
        findings.append(f"Protocol support: {', '.join(found_protocols)}")
        justifications.append(
            {
                "criterion": "protocol_support",
                "points": points,
                "evidence": ", ".join(found_protocols),
                "reasoning": f"{len(found_protocols)} communication protocol(s) detected",
            }
        )
    else:
        justifications.append(
            {
                "criterion": "protocol_support",
                "points": 0,
                "evidence": "file scan",
                "reasoning": "No A2A, ACP, or MCP protocol support detected",
            }
        )

    # --- Additional Detection: Agent Skills ---
    skill_files = [
        f
        for f in root.rglob("SKILL.md")
        if ".venv" not in str(f) and "node_modules" not in str(f)
    ]
    if skill_files:
        details["has_agent_skills"] = True
        details["skill_count"] = len(skill_files)
        details["skill_paths"] = [str(f.relative_to(root)) for f in skill_files[:20]]
        findings.append(
            f"Detected {len(skill_files)} agent skill(s) — will grade in CE-026"
        )
    else:
        details["has_agent_skills"] = False

    # --- Compute grade ---
    grade = _score_to_grade(score)

    return {
        "domain": "Project Analysis",
        "score": score,
        "grade": grade,
        "findings": findings,
        "justifications": justifications,
        "details": details,
    }


def _score_to_grade(score: int) -> str:
    """Convert 0-100 score to letter grade."""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    results = analyze_project(target)
    print(json.dumps(results, indent=2))
