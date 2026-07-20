import os
import re
import subprocess
from pathlib import Path

import pytest


# Paths
TEST_DIR = Path(__file__).resolve().parent
ROOT_DIR = TEST_DIR.parent


def resolve_master_overview() -> Path | None:
    """Locate the sibling registry from a monorepo checkout or Git worktree."""
    candidates: list[Path] = []
    if configured := os.environ.get("AGENT_UTILITIES_OVERVIEW"):
        candidates.append(Path(configured).expanduser())
    for parent in ROOT_DIR.parents:
        candidates.append(parent / "agent-utilities" / "docs" / "overview.md")
    try:
        common_dir = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=ROOT_DIR,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        common_path = Path(common_dir)
        if not common_path.is_absolute():
            common_path = (ROOT_DIR / common_path).resolve()
        canonical_repo = common_path.parent if common_path.name == ".git" else common_path
        if len(canonical_repo.parents) >= 2:
            candidates.append(
                canonical_repo.parents[1]
                / "agent-utilities"
                / "docs"
                / "overview.md"
            )
    except (OSError, subprocess.CalledProcessError):
        pass
    return next((candidate for candidate in candidates if candidate.is_file()), None)


MASTER_OVERVIEW_PATH = resolve_master_overview()


def extract_concepts_from_overview(filepath):
    """Extracts concepts from the markdown table in the master overview.md"""
    if filepath is None or not Path(filepath).is_file():
        return set()

    concepts = set()
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip().startswith("|"):
                continue
            if "Pillar | Sub-Concept" in line or "|---|" in line:
                continue

            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5:
                raw_id = parts[1].replace("*", "").strip()
                if re.match(r"^[A-Z]+-\d+(?:\.\d+)?$", raw_id):
                    concepts.add(raw_id)
    return concepts


def extract_concepts_from_codebase(directory):
    """Recursively scans source files in the project for CONCEPT:ID tags."""
    found_concepts = set()
    for root, _, files in os.walk(directory):
        if (
            "node_modules" in root
            or ".venv" in root
            or ".git" in root
            or "__pycache__" in root
            or f"{os.sep}build{os.sep}" in f"{os.sep}{root}{os.sep}"
        ):
            continue

        for file in files:
            if file.endswith((".py", ".ts", ".tsx", ".md")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        matches = re.findall(r"CONCEPT:([A-Z]+-\d+(?:\.\d+)?)", content)
                        found_concepts.update(matches)
                except Exception:
                    pass
    return found_concepts


def test_concept_parity():
    """
    Enforces that all concepts documented or used in universal-skills
    exist in the master agent-utilities registry.
    """
    if MASTER_OVERVIEW_PATH is None:
        pytest.skip(
            "agent-utilities concept registry is not available; set "
            "AGENT_UTILITIES_OVERVIEW for a standalone checkout"
        )
    master_concepts = extract_concepts_from_overview(MASTER_OVERVIEW_PATH)

    # Extract concepts from this project
    local_codebase_concepts = extract_concepts_from_codebase(ROOT_DIR)

    # Only enforce parity for agent-utilities 5-Pillar concepts
    # Project-specific concepts (SX-*, AU-*, CE-*, TP-*, CA-*, etc.) are excluded
    agent_utilities_pillars = ("ORCH-", "KG-", "AHE-", "ECO-", "OS-")
    local_codebase_concepts = {
        c for c in local_codebase_concepts if c.startswith(agent_utilities_pillars)
    }

    # Ignore legacy KG-00x concepts
    local_codebase_concepts = {
        c for c in local_codebase_concepts if not c.startswith("KG-00")
    }

    # Ensure every concept used locally is registered in the master overview.md
    unregistered_concepts = local_codebase_concepts - master_concepts

    assert not unregistered_concepts, (
        f"The following concepts are used in universal-skills but are NOT registered "
        f"in the master agent-utilities/docs/overview.md registry: {unregistered_concepts}. "
        f"Please register them first."
    )
