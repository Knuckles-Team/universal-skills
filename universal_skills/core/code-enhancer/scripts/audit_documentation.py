#!/usr/bin/env python3
"""FR-006: Documentation governance for code-enhancer skill.

Audits README.md, AGENTS.md, and /docs for completeness, staleness,
and drift against code.

CONCEPT:CE-006 — Documentation & Governance
"""

import json
import re
import subprocess
import sys
from pathlib import Path


DOC_TAXONOMY = {
    "README.md": {"category": "project_overview", "required_sections": [
        "overview", "installation", "usage|quick start"]},
    "AGENTS.md": {"category": "agentic_metadata", "required_sections": [
        "tech stack", "commands", "project structure"]},
    "STANDARDS.md": {"category": "standards", "required_sections": []},
    "CONTRIBUTING.md": {"category": "contributing", "required_sections": []},
    "CHANGELOG.md": {"category": "changelog", "required_sections": []},
    "LICENSE": {"category": "license", "required_sections": []},
}

# Industry-standard README quality criteria (20-point sub-grade)
README_CRITERIA = {
    "has_title": {"weight": 1, "description": "Has an H1 project title"},
    "has_badges": {"weight": 1, "description": "Has CI/version/license badges"},
    "has_description": {"weight": 2, "description": "Has a clear project description (>50 chars)"},
    "has_toc": {"weight": 2, "description": "Has a Table of Contents"},
    "has_installation": {"weight": 2, "description": "Has installation instructions"},
    "has_usage": {"weight": 2, "description": "Has usage examples with code blocks"},
    "has_api_docs": {"weight": 1, "description": "References API/module documentation"},
    "has_architecture": {"weight": 2, "description": "Has architecture overview or diagram"},
    "has_contributing": {"weight": 1, "description": "Has contributing guidelines or link"},
    "has_license": {"weight": 1, "description": "Has license section or reference"},
    "has_code_blocks": {"weight": 1, "description": "Has code examples (fenced blocks)"},
    "has_docs_refs": {"weight": 2, "description": "References /docs directory material"},
    "no_broken_links": {"weight": 1, "description": "No obviously broken markdown links"},
    "reasonable_length": {"weight": 1, "description": "README is between 200-10000 lines"},
}


def _check_doc_completeness(filepath: Path, required_sections: list[str]) -> dict:
    """Check if a doc has required sections."""
    if not filepath.exists():
        return {"exists": False, "missing_sections": required_sections, "size": 0, "headings": []}

    content = filepath.read_text(encoding="utf-8", errors="ignore")
    headings = re.findall(r"^#+\s+(.+)", content, re.MULTILINE)
    headings_lower = [h.lower().strip() for h in headings]

    missing = []
    for section in required_sections:
        # Support pipe-separated aliases (e.g. "usage|quick start")
        aliases = [s.strip() for s in section.split("|")]
        if not any(alias in h for alias in aliases for h in headings_lower):
            missing.append(section)

    return {
        "exists": True,
        "size": len(content),
        "headings": headings[:20],
        "missing_sections": missing,
        "heading_count": len(headings),
    }


def _check_staleness(filepath: Path, root: Path) -> dict:
    """Check document freshness via git blame (last modified date)."""
    if not filepath.exists():
        return {"stale": True, "last_modified": "unknown"}
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci", str(filepath)],
            capture_output=True, text=True, cwd=str(root), timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return {"stale": False, "last_modified": result.stdout.strip()}
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return {"stale": True, "last_modified": "unknown"}


def _detect_code_doc_drift(root: Path) -> list[dict]:
    """Detect drift between code structure and documentation."""
    drift: list[dict] = []

    # Check if AGENTS.md references files that exist
    agents_md = root / "AGENTS.md"
    if agents_md.exists():
        content = agents_md.read_text(encoding="utf-8", errors="ignore")
        # Find file references (paths with extensions)
        file_refs = re.findall(r"`([^`]+\.\w{1,4})`", content)
        for ref in file_refs:
            ref_path = root / ref
            if not ref_path.exists() and not any(
                p.name == Path(ref).name for p in root.rglob(Path(ref).name)
            ):
                drift.append({
                    "type": "broken_reference",
                    "doc": "AGENTS.md",
                    "reference": ref,
                    "detail": f"Referenced file '{ref}' not found in project",
                })

    # Check if README mentions packages/modules that don't exist
    readme = root / "README.md"
    if readme.exists():
        content = readme.read_text(encoding="utf-8", errors="ignore")
        # Look for pip install references
        install_refs = re.findall(r"pip install\s+(\S+)", content)
        # Look for import references
        import_refs = re.findall(r"(?:from|import)\s+(\w+)", content)
        # These are informational, not scored
        if install_refs:
            drift.append({
                "type": "info",
                "doc": "README.md",
                "reference": ", ".join(install_refs[:5]),
                "detail": f"README references {len(install_refs)} install commands",
            })

    return drift


def _grade_readme(root: Path) -> dict:
    """Grade README.md against industry best practices.

    Returns a dict with score (0-20), grade, criteria results, and findings.
    """
    readme_path = root / "README.md"
    if not readme_path.exists():
        return {
            "score": 0, "grade": "F", "max_score": 20,
            "criteria": {k: False for k in README_CRITERIA},
            "findings": ["README.md is missing"],
        }

    content = readme_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    headings = re.findall(r"^#+\s+(.+)", content, re.MULTILINE)
    headings_lower = [h.lower().strip() for h in headings]
    code_blocks = re.findall(r"```\w*\n", content)

    results: dict[str, bool] = {}
    findings: list[str] = []

    # H1 title
    results["has_title"] = bool(re.search(r"^#\s+.+", content, re.MULTILINE))

    # Badges (shields.io, img.shields, badge patterns)
    results["has_badges"] = bool(
        re.search(r"\[!\[.+\]\(.+\)\]|img\.shields\.io|badge", content, re.IGNORECASE)
    )

    # Description (first non-heading, non-blank paragraph > 50 chars)
    first_para = ""
    in_para = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("[!"):
            continue
        if stripped:
            first_para += stripped + " "
            in_para = True
        elif in_para:
            break
    results["has_description"] = len(first_para.strip()) > 50

    # Table of Contents
    results["has_toc"] = any(
        "table of contents" in h or "contents" == h for h in headings_lower
    ) or bool(re.search(r"- \[.+\]\(#.+\)", content))

    # Installation
    results["has_installation"] = any(
        "install" in h for h in headings_lower
    ) or "pip install" in content or "uv pip" in content

    # Usage with code
    results["has_usage"] = any(
        "usage" in h or "quick start" in h or "getting started" in h
        for h in headings_lower
    )

    # API docs reference
    results["has_api_docs"] = any(
        "api" in h or "reference" in h or "module" in h for h in headings_lower
    ) or "docs/" in content

    # Architecture
    results["has_architecture"] = any(
        "architect" in h or "design" in h or "overview" in h for h in headings_lower
    ) or "```mermaid" in content

    # Contributing
    results["has_contributing"] = any(
        "contribut" in h for h in headings_lower
    ) or "CONTRIBUTING.md" in content

    # License
    results["has_license"] = any(
        "license" in h for h in headings_lower
    ) or "LICENSE" in content

    # Code blocks
    results["has_code_blocks"] = len(code_blocks) >= 2

    # Docs references
    results["has_docs_refs"] = bool(
        re.search(r"docs/\w+\.md|\[.+\]\(docs/", content)
    )

    # Broken links (markdown links to files that don't exist)
    md_links = re.findall(r"\[.+?\]\(([^)]+)\)", content)
    broken = 0
    for link in md_links:
        if link.startswith("http") or link.startswith("#") or link.startswith("mailto:"):
            continue
        target = root / link.split("#")[0]
        if not target.exists():
            broken += 1
    results["no_broken_links"] = broken == 0
    if broken > 0:
        findings.append(f"{broken} broken internal links in README.md")

    # Reasonable length
    results["reasonable_length"] = 200 <= len(lines) <= 10000
    if len(lines) < 200:
        findings.append(f"README.md is short ({len(lines)} lines) — consider expanding")
    elif len(lines) > 10000:
        findings.append(f"README.md is very long ({len(lines)} lines) — consider splitting")

    # Score
    score = sum(
        README_CRITERIA[k]["weight"] for k, v in results.items() if v
    )
    max_score = sum(c["weight"] for c in README_CRITERIA.values())
    pct = (score / max_score) * 100 if max_score else 0

    # Generate findings for missing criteria
    for k, v in results.items():
        if not v and README_CRITERIA[k]["weight"] >= 2:
            findings.append(f"README missing: {README_CRITERIA[k]['description']}")

    return {
        "score": score, "max_score": max_score,
        "percentage": round(pct, 1),
        "grade": _score_to_grade(int(pct)),
        "criteria": results,
        "findings": findings,
    }


def _check_docs_directory(root: Path) -> dict:
    """Check /docs directory structure."""
    docs_dir = root / "docs"
    if not docs_dir.is_dir():
        return {"exists": False, "file_count": 0, "files": []}

    doc_files = list(docs_dir.rglob("*.md"))
    return {
        "exists": True,
        "file_count": len(doc_files),
        "files": [str(f.relative_to(root)) for f in doc_files[:20]],
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


def audit_documentation(root_dir: str = ".") -> dict:
    """Audit project documentation and produce scored results."""
    root = Path(root_dir).resolve()
    findings: list[str] = []
    doc_results: dict[str, dict] = {}

    # Check each known doc
    for doc_name, meta in DOC_TAXONOMY.items():
        doc_path = root / doc_name
        completeness = _check_doc_completeness(doc_path, meta["required_sections"])
        staleness = _check_staleness(doc_path, root)
        doc_results[doc_name] = {**completeness, **staleness, "category": meta["category"]}

    # Check /docs
    docs_dir_info = _check_docs_directory(root)
    doc_results["docs/"] = docs_dir_info

    # Drift detection
    drift = _detect_code_doc_drift(root)

    # README grading (industry best practices)
    readme_grade = _grade_readme(root)

    # Scoring
    score = 100

    # README (25 pts — now includes industry grade)
    readme_info = doc_results.get("README.md", {})
    if not readme_info.get("exists"):
        score -= 25
        findings.append("README.md is missing")
    else:
        if readme_info.get("missing_sections"):
            score -= len(readme_info["missing_sections"]) * 3
            findings.append(f"README.md missing sections: {', '.join(readme_info['missing_sections'])}")
        # Industry grade sub-score (up to 15 pts deduction)
        readme_pct = readme_grade.get("percentage", 0)
        if readme_pct < 40:
            score -= 15
        elif readme_pct < 60:
            score -= 10
        elif readme_pct < 80:
            score -= 5
        findings.extend(readme_grade.get("findings", []))

    # AGENTS.md (25 pts)
    agents_info = doc_results.get("AGENTS.md", {})
    if not agents_info.get("exists"):
        score -= 25
        findings.append("AGENTS.md is missing")
    elif agents_info.get("missing_sections"):
        score -= len(agents_info["missing_sections"]) * 5
        findings.append(f"AGENTS.md missing sections: {', '.join(agents_info['missing_sections'])}")

    # /docs directory (20 pts)
    if not docs_dir_info.get("exists"):
        score -= 10
        findings.append("No docs/ directory found")
    elif docs_dir_info.get("file_count", 0) < 3:
        score -= 5

    # Drift (15 pts)
    broken_refs = [d for d in drift if d["type"] == "broken_reference"]
    if len(broken_refs) > 3:
        score -= 15
        findings.append(f"{len(broken_refs)} broken file references in documentation")
    elif len(broken_refs) > 0:
        score -= len(broken_refs) * 3

    # LICENSE (5 pts)
    if not (root / "LICENSE").exists() and not (root / "LICENSE.md").exists():
        score -= 5
        findings.append("No LICENSE file found")

    # CHANGELOG (5 pts)
    if not (root / "CHANGELOG.md").exists():
        score -= 5

    score = max(0, score)

    justifications = [{
        "criterion": "documentation_quality",
        "points": score,
        "evidence": json.dumps({k: {"exists": v.get("exists", False),
                                     "missing": v.get("missing_sections", [])}
                                for k, v in doc_results.items() if isinstance(v, dict)}),
        "reasoning": (f"Audited {len(DOC_TAXONOMY)} standard docs + docs/ directory. "
                      f"{len(broken_refs)} broken references, "
                      f"{sum(1 for d in doc_results.values() if isinstance(d, dict) and d.get('exists'))} docs present. "
                      f"README industry grade: {readme_grade.get('grade', 'N/A')} ({readme_grade.get('percentage', 0)}%)."),
    }]

    return {
        "domain": "Documentation & Governance", "score": score, "grade": _score_to_grade(score),
        "findings": findings, "justifications": justifications,
        "doc_results": doc_results, "drift": drift,
        "readme_grade": readme_grade,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(audit_documentation(target), indent=2))
