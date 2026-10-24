"""Retired builder names must disappear from discovery and published metadata."""

import json
import re
import subprocess
import sys
import tomllib
from configparser import ConfigParser
from pathlib import Path

import pytest

from universal_skills import skill_utilities

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "universal_skills"
RETIRED = {
    "agent-builder",
    "agent-package-builder",
    "api-builder",
    "api-client-builder",
    "api-wrapper-builder",
}


@pytest.mark.parametrize("name", sorted(RETIRED))
def test_retired_builders_are_not_discoverable(name, monkeypatch):
    monkeypatch.setattr(skill_utilities, "files", lambda _: CATALOG)
    monkeypatch.setenv(name.upper().replace("-", "_") + "_ENABLE", "true")
    assert skill_utilities.get_universal_skills_path(name=name) == []
    assert not list(CATALOG.glob("*/" + name))


def test_canonical_builder_is_discoverable_with_resolvable_references(monkeypatch):
    monkeypatch.setattr(skill_utilities, "files", lambda _: CATALOG)
    monkeypatch.setenv("MCP_BUILDER_ENABLE", "true")
    paths = skill_utilities.get_universal_skills_path(name="mcp-builder")
    assert paths == [str(CATALOG / "skills/mcp-builder")]
    skill = Path(paths[0]) / "SKILL.md"
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", skill.read_text()):
        if "://" not in target and not target.startswith("#"):
            assert (skill.parent / target.split("#", 1)[0]).is_file(), target


def test_metadata_no_longer_advertises_retired_builders():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    bump = ConfigParser()
    bump.read(ROOT / ".bumpversion.cfg")
    assert any("mcp-builder/SKILL.md" in section for section in bump.sections())
    extras = project["project"]["optional-dependencies"]
    assert not RETIRED.intersection(extras)
    assert "universal-skills[mcp-builder]>=1.0.0" in extras["all"]
    for filename in ("pyproject.toml", "uv.lock", ".bumpversion.cfg"):
        text = (ROOT / filename).read_text()
        assert not any(name in text for name in RETIRED), filename


def test_current_catalog_and_report_have_only_the_canonical_builder():
    result = subprocess.run(
        [
            sys.executable,
            str(CATALOG / "skills/skill-catalog-auditor/scripts/audit_catalog.py"),
            str(CATALOG),
            "--format",
            "json",
            "--fail-on",
            "error",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    names = {item["name"] for item in json.loads(result.stdout)["skills"]}
    assert "mcp-builder" in names
    assert not names.intersection(RETIRED)
    report = (ROOT / "docs/skill-catalog-audit.md").read_text()
    assert "`mcp-builder`" in report
    assert not any("`" + name + "`" in report for name in RETIRED)
