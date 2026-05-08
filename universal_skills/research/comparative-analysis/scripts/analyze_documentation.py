#!/usr/bin/env python3
"""CA-007: Documentation analysis — README, API docs, architecture, changelog.

Usage: python analyze_documentation.py /path/to/project

CONCEPT:CA-007 — Documentation & Developer Experience
"""

import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".tox", "dist", "build"}

README_CRITERIA = [
    ("title", r"^#\s+.+", 8),
    ("badges", r"\!\[.*?\]\(.*?badge.*?\)", 5),
    ("description", r"(?:description|overview|about)", 8),
    ("table_of_contents", r"(?:table of contents|toc|\-\s+\[)", 5),
    ("installation", r"(?:install|getting started|setup|pip install|npm install)", 10),
    ("usage", r"(?:usage|quick start|example|how to)", 10),
    ("api_docs", r"(?:api|reference|documentation|docs)", 8),
    ("architecture", r"(?:architecture|design|structure|diagram|mermaid)", 8),
    ("contributing", r"(?:contributing|contribute|pull request)", 5),
    ("license", r"(?:license|licence|mit|apache)", 5),
    ("code_blocks", r"```", 8),
    ("links", r"\[.*?\]\(.*?\)", 5),
    ("configuration", r"(?:config|environment|env var|\.env)", 5),
    ("testing", r"(?:test|pytest|jest|npm test)", 5),
    ("changelog_ref", r"(?:changelog|changes|history|what's new)", 5),
]


def grade_readme(project_path: Path) -> dict:
    """Grade README against 15 criteria."""
    for name in ["README.md", "README.rst", "README.txt", "README"]:
        readme_path = project_path / name
        if readme_path.exists():
            try:
                content = readme_path.read_text(errors="ignore")
                break
            except Exception:
                continue
    else:
        return {"score": 0, "found": False, "details": ["No README found"]}

    total = 0
    max_score = sum(c[2] for c in README_CRITERIA)
    details = []
    content_lower = content.lower()

    for criterion, pattern, points in README_CRITERIA:
        if re.search(pattern, content_lower, re.MULTILINE | re.IGNORECASE):
            total += points
            details.append(f"✅ {criterion}: +{points}")
        else:
            details.append(f"❌ {criterion}: +0")

    # Bonus for length
    word_count = len(content.split())
    if word_count >= 1000:
        total += 5
        details.append(f"Comprehensive length ({word_count} words): +5")
    elif word_count >= 300:
        total += 2
        details.append(f"Adequate length ({word_count} words): +2")

    normalized = round(total / max_score * 100) if max_score else 0
    return {
        "score": normalized,
        "found": True,
        "word_count": word_count,
        "details": details,
    }


def analyze_docstrings(project_path: Path) -> dict:
    """Analyze docstring coverage in Python files."""
    import ast

    total_defs = 0
    documented = 0

    for f in project_path.rglob("*.py"):
        rel = f.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        try:
            tree = ast.parse(f.read_text(errors="ignore"))
            for node in ast.walk(tree):
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    total_defs += 1
                    if (
                        node.body
                        and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, (ast.Constant, ast.Str))
                    ):
                        documented += 1
        except (SyntaxError, UnicodeDecodeError):
            pass

    return {
        "total_definitions": total_defs,
        "documented": documented,
        "coverage_pct": round(documented / max(total_defs, 1) * 100, 1),
    }


def check_docs_presence(project_path: Path) -> dict:
    """Check for documentation artifacts."""
    return {
        "docs_directory": (project_path / "docs").is_dir(),
        "changelog": any(
            (project_path / f).exists()
            for f in ["CHANGELOG.md", "CHANGES.md", "HISTORY.md"]
        ),
        "contributing": (project_path / "CONTRIBUTING.md").exists(),
        "agents_md": (project_path / "AGENTS.md").exists(),
        "adr_directory": (project_path / "docs" / "adr").is_dir()
        or (project_path / "doc" / "adr").is_dir(),
        "examples_directory": any(
            (project_path / d).is_dir() for d in ["examples", "example", "demos"]
        ),
        "api_docs": any(
            (project_path / "docs" / f).exists()
            for f in ["api.md", "api-reference.md", "reference.md"]
        )
        if (project_path / "docs").is_dir()
        else False,
    }


def score_documentation(readme: dict, docstrings: dict, presence: dict) -> dict:
    """Calculate 0-100 documentation score."""
    score = 0
    details = []

    # README (35 points)
    readme_score = readme.get("score", 0)
    readme_pts = round(readme_score * 0.35)
    score += readme_pts
    details.append(f"README quality ({readme_score}/100 → {readme_pts}pts)")

    # Docstring coverage (25 points)
    cov = docstrings.get("coverage_pct", 0)
    if cov >= 70:
        score += 25
        details.append(f"Excellent docstring coverage ({cov}%): +25")
    elif cov >= 50:
        score += 18
        details.append(f"Good docstring coverage ({cov}%): +18")
    elif cov >= 30:
        score += 10
        details.append(f"Partial docstring coverage ({cov}%): +10")
    elif cov > 0:
        score += 5
        details.append(f"Minimal docstrings ({cov}%): +5")

    # Documentation artifacts (40 points)
    artifact_scoring = {
        "docs_directory": 10,
        "changelog": 8,
        "contributing": 5,
        "examples_directory": 8,
        "api_docs": 5,
        "agents_md": 2,
        "adr_directory": 2,
    }
    for key, pts in artifact_scoring.items():
        if presence.get(key):
            score += pts
            details.append(f"{key}: +{pts}")

    grade = (
        "A+"
        if score >= 95
        else "A"
        if score >= 90
        else "B+"
        if score >= 85
        else "B"
        if score >= 80
        else "C+"
        if score >= 75
        else "C"
        if score >= 70
        else "D"
        if score >= 60
        else "F"
    )
    return {"score": min(score, 100), "grade": grade, "details": details}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: analyze_documentation.py <project_path>"}))
        sys.exit(1)
    project_path = Path(sys.argv[1]).resolve()
    readme = grade_readme(project_path)
    docstrings = analyze_docstrings(project_path)
    presence = check_docs_presence(project_path)
    scoring = score_documentation(readme, docstrings, presence)

    print(
        json.dumps(
            {
                "domain": "CA-007",
                "domain_name": "Documentation",
                "project": str(project_path),
                "readme": readme,
                "docstrings": docstrings,
                "documentation_artifacts": presence,
                "scoring": scoring,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
