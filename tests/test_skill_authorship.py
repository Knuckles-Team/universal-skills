"""US-CONTENT-R001.6 and US-CONTENT-R001.9: authorship is the organization; skill content is neutral."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "universal_skills" / "skills"
ORG = "Knuckles-Team"
AUTHOR = re.compile(r"^\s*author:\s*(?P<value>.+?)\s*$", re.M)


def _upstream_rendered() -> set[str]:
    manifest = tomllib.loads((ROOT / "upstream-sources.toml").read_text(encoding="utf-8"))
    return {skill["name"] for source in manifest["source"] for skill in source.get("skill", [])}


@pytest.mark.spec("US-CONTENT-R001.6")
def test_first_party_skills_name_the_organization_as_author() -> None:
    rendered = _upstream_rendered()
    wrong = []
    for path in sorted(SKILLS.glob("*/SKILL.md")):
        if path.parent.name in rendered:
            continue
        match = AUTHOR.search(path.read_text(encoding="utf-8").split("\n---", 2)[0])
        if match and match.group("value") != ORG:
            wrong.append(f"{path.parent.name}: {match.group('value')}")
    assert not wrong, wrong
    generators = (
        SKILLS / "skill-builder/scripts/init_skill.py",
        SKILLS / "skill-workflow-builder/scripts/build_workflow.py",
        SKILLS / "mcp-builder/scripts/scaffold_connector.py",
        ROOT / "STANDARDS.md",
    )
    for generator in generators:
        text = generator.read_text(encoding="utf-8")
        assert ORG in text, generator.name
        assert not re.search(r"author\W{1,4}Genius", text), generator.name


@pytest.mark.spec("US-CONTENT-R001.9")
def test_bundled_scripts_hold_no_private_topology_account_or_model() -> None:
    private_address = re.compile(r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b")
    for script in (
        SKILLS / "k8s-node-rolling-update/scripts/roll_update.sh",
        SKILLS / "rotate-credentials/scripts/rotate-credentials.sh",
    ):
        text = script.read_text(encoding="utf-8")
        assert not private_address.search(text), script.name
        assert "genius" not in text.lower(), script.name
    evaluation = (SKILLS / "mcp-builder/scripts/evaluation.py").read_text(encoding="utf-8")
    assert re.search(r'"--model",\s*required=True', evaluation)
    assert not re.search(r"model: str = \"", evaluation)
