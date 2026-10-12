"""Canonical builder resource and retired-catalog packaging contracts."""

from __future__ import annotations

import importlib
import importlib.resources
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READINESS_PACKAGE = "universal_skills.agent-tools.mcp-builder.scripts"
READINESS_RESOURCES = {"agent_readiness.py", "agent_readiness_schema.json"}
RETIRED_SKILLS = {"agent-builder", "agent-package-builder"}


def test_readiness_resources_are_declared_on_their_owning_package() -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    package_data = metadata["tool"]["setuptools"]["package-data"]
    assert READINESS_RESOURCES <= set(package_data[READINESS_PACKAGE])
    extras = metadata["project"]["optional-dependencies"]
    assert not RETIRED_SKILLS.intersection(extras)
    assert "universal-skills[mcp-builder]>=1.0.0" in extras["all"]
    for name in RETIRED_SKILLS:
        assert not any(name in key for key in package_data)
        assert not any("[" + name + "]" in requirement for requirement in extras["all"])


def test_readiness_resources_resolve_through_public_package_path() -> None:
    resources = importlib.resources.files(READINESS_PACKAGE)
    for name in READINESS_RESOURCES:
        assert resources.joinpath(name).is_file()
    schema = json.loads(resources.joinpath("agent_readiness_schema.json").read_text())
    assert schema["$schema"]
    module = importlib.import_module(READINESS_PACKAGE + ".agent_readiness")
    assert callable(module.main)


def test_retired_skill_trees_and_bump_entries_are_absent() -> None:
    catalog = ROOT / "universal_skills" / "agent-tools"
    bump_config = (ROOT / ".bumpversion.cfg").read_text()
    for name in RETIRED_SKILLS:
        assert not (catalog / name).exists()
        assert "/" + name + "/SKILL.md" not in bump_config
