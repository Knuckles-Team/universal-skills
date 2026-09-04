"""Packaging contracts for repository-manager's canonical readiness builder."""

from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
READINESS_PACKAGE = "universal_skills.agent-tools.agent-package-builder.scripts"
READINESS_RESOURCES = {
    "agent_readiness.py",
    "agent_readiness_schema.json",
}


def test_readiness_resources_are_declared_on_their_owning_package() -> None:
    """The authority files must survive wheel and sdist packaging."""

    metadata = tomllib.loads(
        (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    package_data = metadata["tool"]["setuptools"]["package-data"]

    assert READINESS_PACKAGE in package_data
    assert READINESS_RESOURCES <= set(package_data[READINESS_PACKAGE])


def test_declared_readiness_resources_exist_in_source_tree() -> None:
    """Packaging declarations must point at the canonical builder resources."""

    source_dir = ROOT.joinpath(
        "universal_skills",
        "agent-tools",
        "agent-package-builder",
        "scripts",
    )
    assert {
        path.name
        for path in source_dir.iterdir()
        if path.is_file() and path.name in READINESS_RESOURCES
    } == READINESS_RESOURCES
