import re
from pathlib import Path
import json


def analyze_project(root_dir="."):
    root = Path(root_dir)
    report = {
        "project_type": "Unknown",
        "features": [],
        "missing_features": [],
        "architecture_score": 0,
        "details": {},
    }

    # 1. Project Type & Core Dependencies
    pyproject_path = root / "pyproject.toml"
    requirements_path = root / "requirements.txt"

    deps = []
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        deps = re.findall(r'"([^"<>=\s]+)[^"]*"', content)
        report["details"]["has_pyproject"] = True
    elif requirements_path.exists():
        content = requirements_path.read_text()
        deps = re.findall(r"^([^#<>=\s]+)", content, re.MULTILINE)
        report["details"]["has_requirements"] = True

    # Check for core ecosystem markers
    ecosystem_markers = {
        "pydantic-ai": "Pydantic-AI Agent",
        "pydantic-graph": "Graph Agent",
        "fastmcp": "MCP Server",
        "fastapi": "Web Agent/API",
        "agent-utilities": "Agent-Utilities Ecosystem",
    }

    for marker, p_type in ecosystem_markers.items():
        if any(marker in d.lower() for d in deps):
            report["project_type"] = p_type
            report["features"].append(f"Uses {marker}")

    # 2. Architecture & Patterns
    patterns = {
        "Graph Orchestration": (root / "graph_orchestration.py").exists()
        or "pydantic-graph" in deps,
        "Externalized Prompts": (root / "prompts").is_dir()
        or (root / "agent_utilities" / "prompts").is_dir(),
        "Observability (Logfire)": "logfire" in deps
        or "pydantic-ai-slim[logfire]" in deps,
        "A2A Protocol": (root / "a2a.py").exists() or "a2a" in deps,
        "MCP Tools": any(
            f.name.endswith("_mcp.py") or "mcp_server" in f.name
            for f in root.rglob("*.py")
        ),
        "Testing Suite": (root / "tests").is_dir() or "pytest" in deps,
    }

    for feature, exists in patterns.items():
        if exists:
            report["features"].append(feature)
            report["architecture_score"] += 15
        else:
            report["missing_features"].append(feature)

    # 3. Security & DX
    dx_checks = {
        "Standardized AGENTS.md": (root / "AGENTS.md").exists(),
        "Environment Template": (root / ".env.example").exists()
        or (root / ".env.template").exists(),
        "Proper Gitignore": (root / ".gitignore").exists(),
        "Pre-commit Hooks": (root / ".pre-commit-config.yaml").exists(),
    }

    for check, exists in dx_checks.items():
        if exists:
            report["features"].append(check)
            report["architecture_score"] += 10
        else:
            report["missing_features"].append(check)

    return report


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "."
    results = analyze_project(target)
    print(json.dumps(results, indent=2))
