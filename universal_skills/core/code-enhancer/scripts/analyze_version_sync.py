#!/usr/bin/env python3
"""FR-015: Version Synchronization Analysis for code-enhancer skill.

Scans a target repository to ensure that version definitions in code
and documentation (like pyproject.toml, SKILL.md, __init__.py) are
properly tracked within .bumpversion.cfg to prevent version drift.

CONCEPT:CE-022 — Version Synchronization
"""

import json
import re
import sys
from pathlib import Path
import configparser


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


def analyze_version_sync(root_dir: str = ".") -> dict:
    root = Path(root_dir).resolve()
    findings: list[str] = []
    justifications: list[dict] = []
    score = 0
    details: dict = {}

    bump_cfg = root / ".bumpversion.cfg"

    if not bump_cfg.exists():
        return {
            "domain": "Version Sync Analysis",
            "score": 100,  # We don't penalize if they don't use bumpversion
            "grade": "A",
            "findings": ["No .bumpversion.cfg found. Skipping version sync analysis."],
            "justifications": [
                {
                    "criterion": "bumpversion_exists",
                    "points": 100,
                    "evidence": str(bump_cfg),
                    "reasoning": "Project does not use bumpversion.cfg.",
                }
            ],
            "details": {"tracked_files": [], "drifted_files": []},
        }

    score += 20
    justifications.append(
        {
            "criterion": "bumpversion_exists",
            "points": 20,
            "evidence": str(bump_cfg),
            "reasoning": ".bumpversion.cfg found",
        }
    )

    # Parse .bumpversion.cfg
    config = configparser.ConfigParser()
    try:
        config.read(bump_cfg)
    except Exception as e:
        return {
            "domain": "Version Sync Analysis",
            "score": score,
            "grade": "F",
            "findings": [f"Failed to parse .bumpversion.cfg: {e}"],
            "justifications": justifications,
            "details": {"tracked_files": [], "drifted_files": []},
        }

    if "bumpversion" not in config:
        return {
            "domain": "Version Sync Analysis",
            "score": score,
            "grade": "F",
            "findings": ["No [bumpversion] section found in .bumpversion.cfg"],
            "justifications": justifications,
            "details": {"tracked_files": [], "drifted_files": []},
        }

    current_version = config["bumpversion"].get("current_version")
    if not current_version:
        return {
            "domain": "Version Sync Analysis",
            "score": score,
            "grade": "F",
            "findings": ["current_version not defined in .bumpversion.cfg"],
            "justifications": justifications,
            "details": {"tracked_files": [], "drifted_files": []},
        }

    score += 20
    justifications.append(
        {
            "criterion": "current_version_defined",
            "points": 20,
            "evidence": current_version,
            "reasoning": f"Current version tracked is {current_version}",
        }
    )

    # Find tracked files
    tracked_files = []
    for section in config.sections():
        if section.startswith("bumpversion:file:"):
            fname = section.split("bumpversion:file:", 1)[1]
            tracked_files.append(fname)

    details["tracked_files"] = tracked_files

    if not tracked_files:
        justifications.append(
            {
                "criterion": "files_tracked",
                "points": 0,
                "evidence": "0 tracked files",
                "reasoning": "No files are being tracked for version bumping",
            }
        )
        return {
            "domain": "Version Sync Analysis",
            "score": score,
            "grade": "F",
            "findings": ["No files are tracked in .bumpversion.cfg"],
            "justifications": justifications,
            "details": details,
        }

    score += 20
    justifications.append(
        {
            "criterion": "files_tracked",
            "points": 20,
            "evidence": f"{len(tracked_files)} files tracked",
            "reasoning": f"Found {len(tracked_files)} files tracked in .bumpversion.cfg",
        }
    )

    # Search project for current_version
    # We will look in common text files that typically contain versions
    search_extensions = {".py", ".toml", ".md", ".json", ".yaml", ".yml"}
    # Ignore dirs like .git, .venv, build, dist, node_modules
    ignore_dirs = {
        ".git",
        ".venv",
        "venv",
        "env",
        "build",
        "dist",
        "node_modules",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
    }

    drifted_files = []
    total_version_references = 0
    tracked_file_paths = {Path(root / tf).resolve() for tf in tracked_files}

    # Helper regex to check if a line has the version number likely as a version string
    # e.g., version="1.2.3", version : '1.2.3', __version__ = '1.2.3'
    # We use a broad regex matching the exact version near keywords.
    version_pattern = re.compile(
        rf"(version|VERSION)\b.*?['\"]?{re.escape(current_version)}['\"]?"
    )

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        # skip ignored dirs
        if any(part in ignore_dirs for part in path.parts):
            continue

        if path.suffix not in search_extensions:
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        # Look for the current_version string
        if current_version in content:
            # Only consider it a drift if it looks like a version declaration, not just a random mention
            found = False
            for line in content.splitlines():
                if version_pattern.search(line):
                    found = True
                    break

            if found:
                total_version_references += 1
                if path.resolve() not in tracked_file_paths:
                    rel_path = path.relative_to(root).as_posix()
                    drifted_files.append(rel_path)

    details["drifted_files"] = drifted_files

    if drifted_files:
        findings.append(
            f"Found {len(drifted_files)} file(s) with version '{current_version}' that are NOT tracked in .bumpversion.cfg:"
        )
        for df in drifted_files[:5]:
            findings.append(f"  - {df}")
        if len(drifted_files) > 5:
            findings.append(f"  ... and {len(drifted_files) - 5} more.")

        justifications.append(
            {
                "criterion": "version_drift_check",
                "points": 0,
                "evidence": f"{len(drifted_files)} untracked files",
                "reasoning": "Version definitions found in codebase that are missing from .bumpversion.cfg",
            }
        )
    else:
        score += 40
        findings.append(
            f"All version '{current_version}' declarations appear to be tracked correctly."
        )
        justifications.append(
            {
                "criterion": "version_drift_check",
                "points": 40,
                "evidence": "0 drifted files",
                "reasoning": "No version drift detected in codebase files",
            }
        )

    return {
        "domain": "Version Sync Analysis",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": justifications,
        "details": details,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    results = analyze_version_sync(target)
    print(json.dumps(results, indent=2))
