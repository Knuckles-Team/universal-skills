#!/usr/bin/env python3
"""CE-017: Directory organization analysis for code-enhancer skill.

Measures files-per-directory, depth distribution, and monolithic directory
patterns to detect flat/bloated directory structures. Generates actionable
reorganization suggestions.

CONCEPT:CE-017 — Directory Organization
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

_SKIP_DIRS = frozenset({
    ".venv", "venv", "__pycache__", "node_modules", ".git",
    "build", "dist", ".tox", ".mypy_cache", ".ruff_cache",
    ".pytest_cache", "target", ".gradle", ".idea", ".vscode",
    "egg-info", ".eggs", ".cache",
})

# Source file extensions to count (not configs, not binary)
_SOURCE_EXTENSIONS = frozenset({
    ".py", ".pyi", ".go", ".js", ".jsx", ".ts", ".tsx", ".rs",
    ".java", ".kt", ".kts", ".rb", ".cs", ".cpp", ".c", ".h",
    ".html", ".css", ".scss", ".vue", ".svelte", ".sh", ".sql",
    ".yaml", ".yml", ".toml", ".json", ".md", ".rst",
})

# Rogue/throwaway script prefixes that should not be in the codebase
_ROGUE_PREFIXES = (
    "fix_", "validate_", "cleanup_", "patch_", "repair_",
    "resolve_", "debug_", "tmp_", "temp_", "hack_",
)


def _should_skip(path: Path) -> bool:
    """Check if any path component is in the skip set."""
    return any(part in _SKIP_DIRS for part in path.parts)


def _detect_rogue_scripts(root: Path) -> list[dict]:
    """Detect throwaway/rogue scripts that pollute the codebase."""
    rogue_files: list[dict] = []
    for f in root.rglob("*.py"):
        if _should_skip(f):
            continue
        name = f.name.lower()
        for prefix in _ROGUE_PREFIXES:
            if name.startswith(prefix):
                rogue_files.append({
                    "file": str(f.relative_to(root)),
                    "prefix": prefix.rstrip("_"),
                    "recommendation": "Remove or integrate into project modules",
                })
                break
    return rogue_files


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


def analyze_directory_density(root_dir: str = ".") -> dict:
    """Analyze directory organization and produce scored results.

    Metrics:
        - Files per directory (crowded > 20, severely crowded > 40)
        - Max directory depth (too flat < 2, too deep > 8)
        - Monolithic concentration (single dir > 50% of all files)
        - Empty directories
        - Suggested reorganizations for crowded directories

    Returns:
        dict with domain, score, grade, findings, metrics, suggestions.
    """
    root = Path(root_dir).resolve()

    # Collect files per directory
    dir_files: dict[str, list[str]] = defaultdict(list)
    all_files: list[Path] = []
    dir_depths: list[int] = []
    empty_dirs: list[str] = []

    for f in root.rglob("*"):
        if _should_skip(f):
            continue
        if f.is_file() and f.suffix.lower() in _SOURCE_EXTENSIONS:
            rel_parent = str(f.parent.relative_to(root))
            dir_files[rel_parent].append(f.name)
            all_files.append(f)
            depth = len(f.relative_to(root).parts) - 1
            dir_depths.append(depth)

    # Find empty directories (that aren't skip dirs)
    for d in root.rglob("*"):
        if d.is_dir() and not _should_skip(d):
            children = [c for c in d.iterdir()
                        if c.is_file() and c.suffix.lower() in _SOURCE_EXTENSIONS]
            if not children and not any(c.is_dir() for c in d.iterdir()
                                         if not _should_skip(c)):
                empty_dirs.append(str(d.relative_to(root)))

    if not all_files:
        return {
            "domain": "Directory Organization",
            "score": 50,
            "grade": "F",
            "findings": ["No source files found to analyze"],
            "justifications": [],
            "metrics": {},
            "crowded_dirs": [],
            "suggestions": [],
        }

    total_files = len(all_files)
    max_depth = max(dir_depths) if dir_depths else 0
    avg_depth = sum(dir_depths) / len(dir_depths) if dir_depths else 0

    # Identify crowded directories
    crowded_dirs = []
    severely_crowded_dirs = []
    for dir_path, files in sorted(dir_files.items(), key=lambda x: len(x[1]), reverse=True):
        count = len(files)
        if count > 40:
            severely_crowded_dirs.append({"directory": dir_path, "file_count": count, "files": files[:10]})
        elif count > 20:
            crowded_dirs.append({"directory": dir_path, "file_count": count, "files": files[:10]})

    # Monolithic check: single dir holds > 50% of files
    monolithic_dirs = []
    for dir_path, files in dir_files.items():
        ratio = len(files) / total_files
        if ratio > 0.50 and len(files) > 15:
            monolithic_dirs.append({
                "directory": dir_path,
                "file_count": len(files),
                "percentage": round(ratio * 100, 1),
            })

    # Generate reorganization suggestions
    suggestions: list[dict] = []
    for item in severely_crowded_dirs + crowded_dirs:
        dir_path = item["directory"]
        files = item["files"]
        count = item["file_count"]

        # Group files by prefix pattern to suggest subdirectories
        prefix_groups: dict[str, int] = defaultdict(int)
        for fname in dir_files[dir_path]:
            # Extract common prefix (e.g., "test_" → "tests", "analyze_" → "analyzers")
            parts = fname.replace(".py", "").replace(".ts", "").replace(".js", "").split("_")
            if len(parts) >= 2:
                prefix_groups[parts[0]] += 1

        suggested_subdirs = [
            prefix for prefix, c in prefix_groups.items()
            if c >= 3 and prefix not in ("__init__", "test")
        ]

        suggestions.append({
            "directory": dir_path,
            "current_count": count,
            "action": f"Consider splitting {count} files into subdirectories",
            "suggested_groups": suggested_subdirs[:5] if suggested_subdirs else ["by-feature", "by-domain"],
        })

    # Scoring (start at 100, deduct)
    score = 100
    findings: list[str] = []

    # Severely crowded penalty
    if severely_crowded_dirs:
        penalty = min(30, len(severely_crowded_dirs) * 10)
        score -= penalty
        findings.append(
            f"{len(severely_crowded_dirs)} directories with >40 files: "
            + ", ".join(d["directory"] for d in severely_crowded_dirs[:3])
        )

    # Crowded penalty
    if crowded_dirs:
        penalty = min(25, len(crowded_dirs) * 5)
        score -= penalty
        findings.append(
            f"{len(crowded_dirs)} directories with >20 files: "
            + ", ".join(d["directory"] for d in crowded_dirs[:3])
        )

    # Depth penalties
    if max_depth < 2 and total_files > 20:
        score -= 10
        findings.append(f"Flat project structure (max depth {max_depth}) with {total_files} files")
    elif max_depth > 8:
        score -= 10
        findings.append(f"Deeply nested project structure (max depth {max_depth})")

    # Monolithic penalty
    if monolithic_dirs:
        score -= 15
        for md in monolithic_dirs:
            findings.append(
                f"Monolithic directory: {md['directory']} contains "
                f"{md['percentage']}% of all files ({md['file_count']}/{total_files})"
            )

    # Rogue script detection
    rogue_scripts = _detect_rogue_scripts(root)
    if rogue_scripts:
        rogue_penalty = min(15, len(rogue_scripts) * 3)
        score -= rogue_penalty
        rogue_names = [r["file"] for r in rogue_scripts[:5]]
        findings.append(
            f"{len(rogue_scripts)} rogue/throwaway scripts detected "
            f"(fix_*, validate_*, patch_*, etc.): {', '.join(rogue_names)}"
        )

    score = max(0, score)

    metrics = {
        "total_source_files": total_files,
        "total_directories": len(dir_files),
        "max_depth": max_depth,
        "avg_depth": round(avg_depth, 1),
        "crowded_dirs_20plus": len(crowded_dirs),
        "severely_crowded_40plus": len(severely_crowded_dirs),
        "monolithic_dirs": len(monolithic_dirs),
        "empty_dirs": len(empty_dirs),
        "avg_files_per_dir": round(total_files / max(len(dir_files), 1), 1),
        "rogue_scripts": len(rogue_scripts),
    }

    justifications = [{
        "criterion": "directory_organization",
        "points": score,
        "evidence": json.dumps(metrics),
        "reasoning": (
            f"{total_files} files across {len(dir_files)} directories. "
            f"Max depth: {max_depth}, avg files/dir: {metrics['avg_files_per_dir']}. "
            f"{len(crowded_dirs)} crowded, {len(severely_crowded_dirs)} severely crowded, "
            f"{len(monolithic_dirs)} monolithic, "
            f"{len(rogue_scripts)} rogue scripts."
        ),
    }]

    return {
        "domain": "Directory Organization",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": justifications,
        "metrics": metrics,
        "crowded_dirs": severely_crowded_dirs + crowded_dirs,
        "monolithic_dirs": monolithic_dirs,
        "suggestions": suggestions,
        "rogue_scripts": rogue_scripts,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(analyze_directory_density(target), indent=2))
