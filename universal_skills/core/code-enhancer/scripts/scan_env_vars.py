#!/usr/bin/env python3
"""CE-025: Environment variable scanner for code-enhancer skill.

Scans the codebase for all environment variable usage across Python source,
Dockerfiles, docker-compose/compose.yml, .env, and .env.example files.
Cross-references against README.md documentation to identify undocumented vars.

CONCEPT:CE-025 — Environment Variable Scanning
"""

import json
import re
import sys
from pathlib import Path


# Patterns for extracting env vars from Python source
PYTHON_PATTERNS = [
    # os.getenv("VAR", default)
    re.compile(r"""os\.getenv\(\s*['\"](\w+)['\"]"""),
    # os.environ.get("VAR", default)
    re.compile(r"""os\.environ\.get\(\s*['\"](\w+)['\"]"""),
    # os.environ["VAR"]
    re.compile(r"""os\.environ\[\s*['\"](\w+)['\"]"""),
    # os.environ.pop("VAR", ...)
    re.compile(r"""os\.environ\.pop\(\s*['\"](\w+)['\"]"""),
    # os.environ.setdefault("VAR", ...)
    re.compile(r"""os\.environ\.setdefault\(\s*['\"](\w+)['\"]"""),
]

# Patterns for Dockerfile ENV directives
DOCKERFILE_PATTERNS = [
    # ENV VAR=value
    re.compile(r"^ENV\s+(\w+)=", re.MULTILINE),
    # ENV VAR value
    re.compile(r"^ENV\s+(\w+)\s+(?!=)", re.MULTILINE),
    # ARG VAR=default
    re.compile(r"^ARG\s+(\w+)", re.MULTILINE),
]

# Patterns for docker-compose/compose.yml
COMPOSE_ENV_PATTERN = re.compile(r"^\s*-?\s*(\w+)=", re.MULTILINE)
COMPOSE_ENV_KEY_PATTERN = re.compile(r"^\s*(\w+):", re.MULTILINE)


def _scan_python_files(root: Path) -> list[dict]:
    """Scan all Python files for environment variable usage."""
    results: list[dict] = []
    py_files = [
        f
        for f in root.rglob("*.py")
        if ".venv" not in f.parts
        and "__pycache__" not in f.parts
        and "node_modules" not in f.parts
        and ".git" not in f.parts
    ]

    for filepath in py_files:
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for line_num, line in enumerate(content.splitlines(), 1):
            for pattern in PYTHON_PATTERNS:
                for match in pattern.finditer(line):
                    var_name = match.group(1)

                    # Try to extract default value
                    default = None
                    # Look for the second argument in getenv/get calls
                    full_match = line[match.start() :]
                    default_match = re.search(
                        r""",\s*['\"]?([^'\")\s,]+)['\"]?""",
                        full_match[len(match.group(0)) :],
                    )
                    if default_match:
                        default = default_match.group(1)

                    results.append(
                        {
                            "var_name": var_name,
                            "source": str(filepath.relative_to(root)),
                            "line": line_num,
                            "source_type": "python",
                            "default": default,
                            "context": line.strip()[:120],
                        }
                    )

    return results


def _scan_dockerfiles(root: Path) -> list[dict]:
    """Scan Dockerfiles for ENV and ARG directives."""
    results: list[dict] = []
    dockerfile_names = [
        "Dockerfile",
        "dockerfile",
        "Dockerfile.dev",
        "Dockerfile.prod",
        "debug.Dockerfile",
    ]

    for name in dockerfile_names:
        for filepath in root.rglob(name):
            if ".venv" not in filepath.parts and ".git" not in filepath.parts:
                try:
                    content = filepath.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

                for pattern in DOCKERFILE_PATTERNS:
                    for match in pattern.finditer(content):
                        var_name = match.group(1)
                        # Find line number
                        line_num = content[: match.start()].count("\n") + 1
                        results.append(
                            {
                                "var_name": var_name,
                                "source": str(filepath.relative_to(root)),
                                "line": line_num,
                                "source_type": "dockerfile",
                                "default": None,
                                "context": content.splitlines()[line_num - 1].strip()[
                                    :120
                                ]
                                if line_num <= len(content.splitlines())
                                else "",
                            }
                        )

    return results


def _scan_compose_files(root: Path) -> list[dict]:
    """Scan docker-compose/compose.yml for environment variables."""
    results: list[dict] = []
    compose_names = [
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",
        "mcp.compose.yml",
    ]

    for name in compose_names:
        filepath = root / name
        if not filepath.exists():
            continue

        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Look for environment: sections
        in_env_section = False
        for line_num, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("environment:"):
                in_env_section = True
                continue
            if in_env_section:
                if stripped.startswith("-") or ":" in stripped:
                    # Extract var name
                    env_match = re.match(r"-?\s*(\w+)[=:]", stripped)
                    if env_match:
                        var_name = env_match.group(1)
                        results.append(
                            {
                                "var_name": var_name,
                                "source": name,
                                "line": line_num,
                                "source_type": "compose",
                                "default": None,
                                "context": stripped[:120],
                            }
                        )
                elif not stripped.startswith("#") and stripped and not stripped.startswith("-"):
                    in_env_section = False

    return results


def _scan_dotenv_files(root: Path) -> list[dict]:
    """Scan .env and .env.example files."""
    results: list[dict] = []
    env_files = [".env", ".env.example", ".env.template", ".env.local"]

    for name in env_files:
        filepath = root / name
        if not filepath.exists():
            continue

        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for line_num, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                match = re.match(r"(\w+)\s*=\s*(.*)", stripped)
                if match:
                    var_name = match.group(1)
                    default = match.group(2).strip().strip("\"'") or None
                    results.append(
                        {
                            "var_name": var_name,
                            "source": name,
                            "line": line_num,
                            "source_type": "dotenv",
                            "default": default,
                            "context": stripped[:120],
                        }
                    )

    return results


def _check_readme_docs(root: Path, all_vars: set[str]) -> dict:
    """Check if environment variables are documented in README.md."""
    readme = root / "README.md"
    documented: set[str] = set()
    undocumented: set[str] = set()

    if readme.exists():
        try:
            content = readme.read_text(encoding="utf-8", errors="ignore")
            for var in all_vars:
                if var in content:
                    documented.add(var)
                else:
                    undocumented.add(var)
        except Exception:
            undocumented = all_vars
    else:
        undocumented = all_vars

    return {
        "documented": sorted(documented),
        "undocumented": sorted(undocumented),
        "coverage": len(documented) / max(len(all_vars), 1),
    }


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


def scan_env_vars(root_dir: str = ".") -> dict:
    """Scan project for environment variable usage and documentation.

    Returns:
        dict with all found env vars, documentation status, and scoring.
    """
    root = Path(root_dir).resolve()
    findings: list[str] = []

    # Scan all sources
    python_vars = _scan_python_files(root)
    dockerfile_vars = _scan_dockerfiles(root)
    compose_vars = _scan_compose_files(root)
    dotenv_vars = _scan_dotenv_files(root)

    all_occurrences = python_vars + dockerfile_vars + compose_vars + dotenv_vars

    # Consolidate unique var names
    var_details: dict[str, dict] = {}
    for occ in all_occurrences:
        name = occ["var_name"]
        if name not in var_details:
            var_details[name] = {
                "name": name,
                "sources": [],
                "defaults": [],
                "source_types": set(),
            }
        var_details[name]["sources"].append(
            f"{occ['source']}:{occ['line']}"
        )
        var_details[name]["source_types"].add(occ["source_type"])
        if occ["default"]:
            var_details[name]["defaults"].append(occ["default"])

    # Convert sets to lists for JSON
    for v in var_details.values():
        v["source_types"] = sorted(v["source_types"])
        v["sources"] = v["sources"][:5]  # Limit
        v["defaults"] = list(set(v["defaults"]))[:3]

    all_var_names = set(var_details.keys())

    # Check README documentation
    readme_check = _check_readme_docs(root, all_var_names)

    # Check .env.example coverage
    dotenv_var_names = {v["var_name"] for v in dotenv_vars}
    python_var_names = {v["var_name"] for v in python_vars}
    env_example_missing = python_var_names - dotenv_var_names

    # Scoring
    score = 100

    if not all_var_names:
        # No env vars found — neutral score
        return {
            "domain": "Environment Variables",
            "score": 85,
            "grade": "B",
            "findings": ["No environment variables detected in codebase"],
            "justifications": [
                {
                    "criterion": "env_var_documentation",
                    "points": 85,
                    "evidence": str(root),
                    "reasoning": "No environment variables found — not applicable.",
                }
            ],
            "metrics": {"total_vars": 0},
            "variables": {},
        }

    # Documentation coverage
    doc_coverage = readme_check["coverage"]
    if doc_coverage < 0.3:
        score -= 30
        findings.append(
            f"Only {doc_coverage:.0%} of env vars documented in README.md"
        )
    elif doc_coverage < 0.6:
        score -= 15
        findings.append(
            f"Partial env var documentation: {doc_coverage:.0%} coverage"
        )
    elif doc_coverage < 0.9:
        score -= 5

    # Undocumented vars
    if readme_check["undocumented"]:
        findings.append(
            f"Undocumented env vars: {', '.join(readme_check['undocumented'][:10])}"
        )

    # .env.example coverage
    if (root / ".env.example").exists():
        if env_example_missing:
            missing_count = len(env_example_missing)
            score -= min(10, missing_count * 2)
            findings.append(
                f"{missing_count} Python env vars not in .env.example: "
                f"{', '.join(sorted(env_example_missing)[:5])}"
            )
    elif python_var_names:
        score -= 10
        findings.append(
            "No .env.example file — create one for developer onboarding"
        )

    # Vars without defaults
    no_default = [
        name
        for name, info in var_details.items()
        if not info["defaults"] and "python" in info["source_types"]
    ]
    if len(no_default) > 5:
        score -= 5
        findings.append(
            f"{len(no_default)} env vars have no default value in code"
        )

    score = max(0, score)

    metrics = {
        "total_vars": len(all_var_names),
        "python_vars": len(python_var_names),
        "dockerfile_vars": len({v["var_name"] for v in dockerfile_vars}),
        "compose_vars": len({v["var_name"] for v in compose_vars}),
        "dotenv_vars": len(dotenv_var_names),
        "readme_documented": len(readme_check["documented"]),
        "readme_undocumented": len(readme_check["undocumented"]),
        "documentation_coverage": round(doc_coverage, 2),
    }

    justifications = [
        {
            "criterion": "env_var_documentation",
            "points": score,
            "evidence": json.dumps(metrics),
            "reasoning": (
                f"Found {len(all_var_names)} unique env vars across "
                f"{len(all_occurrences)} occurrences. "
                f"README documents {len(readme_check['documented'])}/{len(all_var_names)}. "
                f"{'Has' if (root / '.env.example').exists() else 'Missing'} .env.example."
            ),
        }
    ]

    return {
        "domain": "Environment Variables",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": justifications,
        "metrics": metrics,
        "variables": var_details,
        "readme_coverage": readme_check,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(scan_env_vars(target), indent=2))
