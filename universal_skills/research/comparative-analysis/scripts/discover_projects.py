#!/usr/bin/env python3
"""CA-000: Auto-discover project metadata for comparative analysis.

Accepts N project paths and extracts: name, version, description, license,
language ecosystem, dependencies, and basic structure metrics.

Usage:
    python discover_projects.py /path/to/project1 /path/to/project2 [...]
    python discover_projects.py --mode research /path/to/paper1.md /path/to/paper2.pdf

CONCEPT:CA-000 — Project Discovery & Classification
"""

import json
import re
import sys
import tomllib
import uuid
from pathlib import Path

LANGUAGE_MARKERS = {
    "python": [
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "requirements.txt",
        "Pipfile",
    ],
    "node": ["package.json", "tsconfig.json", "yarn.lock", "pnpm-lock.yaml"],
    "go": ["go.mod", "go.sum"],
    "rust": ["Cargo.toml", "Cargo.lock"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
}

RESEARCH_EXTENSIONS = {".md", ".pdf", ".txt", ".tex", ".rst", ".html"}


def detect_language(project_path: Path) -> str:
    """Detect primary language ecosystem."""
    for lang, markers in LANGUAGE_MARKERS.items():
        for marker in markers:
            if (project_path / marker).exists():
                return lang
    # Fallback: count file extensions
    ext_counts: dict[str, int] = {}
    for f in project_path.rglob("*"):
        if f.is_file() and not any(
            p in str(f) for p in [".git", "node_modules", "__pycache__", ".venv"]
        ):
            ext_counts[f.suffix] = ext_counts.get(f.suffix, 0) + 1
    ext_to_lang = {
        ".py": "python",
        ".js": "node",
        ".ts": "node",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
    }
    best = max(ext_counts, key=ext_counts.get, default="")
    return ext_to_lang.get(best, "unknown")


def extract_python_metadata(project_path: Path) -> dict:
    """Extract metadata from pyproject.toml."""
    pyproject = project_path / "pyproject.toml"
    if not pyproject.exists():
        return {}
    try:
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
        proj = data.get("project", {})
        deps = []
        for d in proj.get("dependencies", []):
            name = re.split(r"[<>=~!\[;]", d)[0].strip()
            if name:
                deps.append(name.lower())
        return {
            "name": proj.get("name", ""),
            "version": proj.get("version", ""),
            "description": proj.get("description", ""),
            "license": proj.get("license", {}).get("text", "")
            if isinstance(proj.get("license"), dict)
            else str(proj.get("license", "")),
            "dependencies": deps,
            "dep_count": len(deps),
            "python_requires": proj.get("requires-python", ""),
        }
    except Exception as e:
        return {"error": str(e)}


def extract_node_metadata(project_path: Path) -> dict:
    """Extract metadata from package.json."""
    pkg = project_path / "package.json"
    if not pkg.exists():
        return {}
    try:
        data = json.loads(pkg.read_text())
        deps = list(data.get("dependencies", {}).keys())
        dev_deps = list(data.get("devDependencies", {}).keys())
        return {
            "name": data.get("name", ""),
            "version": data.get("version", ""),
            "description": data.get("description", ""),
            "license": data.get("license", ""),
            "dependencies": deps,
            "dev_dependencies": dev_deps,
            "dep_count": len(deps),
        }
    except Exception as e:
        return {"error": str(e)}


def count_structure(project_path: Path) -> dict:
    """Count files, directories, and lines of code."""
    file_count = 0
    dir_count = 0
    total_loc = 0
    ext_counts: dict[str, int] = {}
    skip = {".git", "node_modules", "__pycache__", ".venv", ".tox", "dist", "build"}
    for item in project_path.rglob("*"):
        rel_parts = item.relative_to(project_path).parts
        if any(p in skip for p in rel_parts):
            continue
        if item.is_dir():
            dir_count += 1
        elif item.is_file():
            file_count += 1
            ext_counts[item.suffix] = ext_counts.get(item.suffix, 0) + 1
            if item.suffix in {
                ".py",
                ".js",
                ".ts",
                ".go",
                ".rs",
                ".java",
                ".c",
                ".cpp",
                ".h",
            }:
                try:
                    total_loc += sum(1 for _ in open(item, errors="ignore"))
                except (OSError, UnicodeDecodeError):
                    pass
    return {
        "file_count": file_count,
        "dir_count": dir_count,
        "total_loc": total_loc,
        "extension_distribution": dict(
            sorted(ext_counts.items(), key=lambda x: -x[1])[:10]
        ),
    }


def is_research_item(path: Path) -> bool:
    """Check if a path is a research paper/document rather than a codebase."""
    if path.is_file():
        return path.suffix.lower() in RESEARCH_EXTENSIONS
    # Check if directory contains mostly docs
    if path.is_dir():
        doc_count = sum(
            1 for f in path.rglob("*") if f.suffix.lower() in RESEARCH_EXTENSIONS
        )
        code_count = sum(
            1
            for f in path.rglob("*")
            if f.suffix.lower() in {".py", ".js", ".ts", ".go", ".rs", ".java"}
        )
        return doc_count > code_count * 2
    return False


def discover_project(path: Path) -> dict:
    """Discover metadata for a single project or research item."""
    result = {
        "path": str(path.resolve()),
        "name": path.name,
        "exists": path.exists(),
    }
    if not path.exists():
        result["error"] = "Path does not exist"
        return result

    if is_research_item(path):
        result["type"] = "research"
        if path.is_file():
            result["format"] = path.suffix.lower()
            try:
                content = path.read_text(errors="ignore")
                result["char_count"] = len(content)
                result["word_count"] = len(content.split())
                result["line_count"] = content.count("\n")
            except Exception:
                pass
        else:
            docs = list(path.rglob("*"))
            result["document_count"] = len([d for d in docs if d.is_file()])
        return result

    result["type"] = "codebase"
    result["language"] = detect_language(path)
    result["structure"] = count_structure(path)

    # License detection
    for lf in ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "LICENCE"]:
        if (path / lf).exists():
            result["license_file"] = lf
            try:
                content = (path / lf).read_text(errors="ignore")[:500]
                if "MIT" in content:
                    result["license_detected"] = "MIT"
                elif "Apache" in content:
                    result["license_detected"] = "Apache-2.0"
                elif "GNU GENERAL PUBLIC" in content.upper():
                    result["license_detected"] = "GPL"
                elif "BSD" in content:
                    result["license_detected"] = "BSD"
            except Exception:
                pass
            break

    # Language-specific metadata
    if result["language"] == "python":
        result["metadata"] = extract_python_metadata(path)
    elif result["language"] == "node":
        result["metadata"] = extract_node_metadata(path)
    else:
        result["metadata"] = {}

    # Key file detection
    key_files = {
        "readme": any(
            (path / f).exists()
            for f in ["README.md", "README.rst", "README.txt", "README"]
        ),
        "changelog": any(
            (path / f).exists() for f in ["CHANGELOG.md", "CHANGES.md", "HISTORY.md"]
        ),
        "contributing": (path / "CONTRIBUTING.md").exists(),
        "code_of_conduct": any(
            (path / f).exists()
            for f in ["CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"]
        ),
        "security_policy": any(
            (path / f).exists() for f in ["SECURITY.md", ".github/SECURITY.md"]
        ),
        "ci_config": any(
            (path / f).exists()
            for f in [
                ".github/workflows",
                ".gitlab-ci.yml",
                "Jenkinsfile",
                ".circleci/config.yml",
            ]
        ),
        "docker": any(
            (path / f).exists()
            for f in ["Dockerfile", "docker-compose.yml", "compose.yml"]
        ),
        "tests": any(
            (path / f).exists() for f in ["tests", "test", "spec", "__tests__"]
        ),
        "docs": any((path / f).exists() for f in ["docs", "doc", "documentation"]),
        "agents_md": (path / "AGENTS.md").exists(),
    }
    result["key_files"] = key_files

    return result


def main():
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "error": "Usage: discover_projects.py <path1> [path2] [--kg-query <query>] [--mode <mode>]"
                }
            )
        )
        sys.exit(1)

    # Check for --mode and --kg-query flags
    mode = "auto"
    kg_query = ""
    session_id = uuid.uuid4().hex[:8]
    temp_dir = Path.cwd() / ".specify" / "ca_repos" / session_id
    cleanup_needed = False

    paths = []
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--mode" and i + 1 < len(sys.argv):
            mode = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--kg-query" and i + 1 < len(sys.argv):
            kg_query = sys.argv[i + 1]
            i += 2
        else:
            arg = sys.argv[i]
            i += 1
            if arg.startswith(("http://", "https://", "git@")):
                try:
                    import repository_manager

                    temp_dir.mkdir(parents=True, exist_ok=True)
                    repo_name = arg.rstrip("/").split("/")[-1]
                    if repo_name.endswith(".git"):
                        repo_name = repo_name[:-4]
                    target_path = temp_dir / repo_name
                    print(f"Cloning {arg} into {target_path}...", file=sys.stderr)
                    git = repository_manager.Git()
                    res = git.clone_repository(arg, str(target_path))
                    if res.status == "success":
                        paths.append(str(target_path))
                        cleanup_needed = True
                    else:
                        print(f"Failed to clone {arg}: {res.error}", file=sys.stderr)
                except ImportError:
                    print(
                        f"repository-manager not installed, cannot clone {arg}",
                        file=sys.stderr,
                    )
            else:
                paths.append(arg)

    projects = []

    # Resolve KG sources if --kg-query is provided (CONCEPT:KG-2.12)
    if kg_query:
        kg_sources = _resolve_kg_sources(kg_query)
        for src in kg_sources:
            projects.append(
                {
                    "path": src.get("file_path", ""),
                    "name": src.get("name", ""),
                    "type": src.get("source_type", "research"),
                    "exists": Path(src.get("file_path", "")).exists()
                    if src.get("file_path")
                    else False,
                    "source": "knowledge_graph",
                    "kg_metadata": src.get("kg_metadata", {}),
                    "relevance_score": src.get("relevance_score", 0.0),
                }
            )

    # Discover filesystem projects
    for p in paths:
        path = Path(p).resolve()
        project = discover_project(path)
        if mode == "research":
            project["type"] = "research"
        project["source"] = "filesystem"
        projects.append(project)

    # Determine analysis mode
    types = {p["type"] for p in projects if "type" in p}
    if types == {"codebase"}:
        analysis_mode = "codebase"
    elif types == {"research"}:
        analysis_mode = "research"
    else:
        analysis_mode = "hybrid"

    output = {
        "analysis_mode": analysis_mode,
        "project_count": len(projects),
        "kg_query": kg_query if kg_query else None,
        "projects": projects,
    }

    if cleanup_needed:
        output["cleanup_instruction"] = (
            f"After analysis, delete the temporary directory: {temp_dir}"
        )
        print(
            f"\\n[!] Note: Cloned remote repositories into {temp_dir}. Please clean up after analysis.",
            file=sys.stderr,
        )

    print(json.dumps(output, indent=2))


def _resolve_kg_sources(query: str) -> list[dict]:
    """Resolve sources from the Knowledge Graph (CONCEPT:KG-2.12).

    This is optional — if agent_utilities is not installed or no KG
    engine is available, returns an empty list gracefully.

    Args:
        query: Search query for KG resolution.

    Returns:
        List of resolved source dicts with file_path, name, source_type.
    """
    try:
        from agent_utilities.knowledge_graph.source_resolver import KGSourceResolver
        from agent_utilities.knowledge_graph.engine import IntelligenceGraphEngine

        engine = IntelligenceGraphEngine.get_active()
        if not engine:
            print(
                json.dumps(
                    {"kg_warning": "No active KG engine — skipping KG resolution"}
                ),
                file=sys.stderr,
            )
            return []

        resolver = KGSourceResolver(engine=engine)
        resolved = resolver.resolve_any(query=query, top_k=10)
        return [r.model_dump() for r in resolved]
    except ImportError:
        print(
            json.dumps(
                {
                    "kg_warning": "agent_utilities not installed — KG resolution unavailable"
                }
            ),
            file=sys.stderr,
        )
        return []
    except Exception as e:
        print(json.dumps({"kg_warning": f"KG resolution failed: {e}"}), file=sys.stderr)
        return []


if __name__ == "__main__":
    main()
