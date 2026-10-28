"""US-CONTENT: the package is served by the SDK content convention."""

from __future__ import annotations

import asyncio
import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "universal_skills"
SKILLS = PKG / "skills"
GROUP = "agent_connector_sdk.connector"


def _folders() -> list[Path]:
    return sorted(p.parent for p in SKILLS.glob("*/SKILL.md"))


@pytest.mark.spec("US-CONTENT-R001.1")
def test_declares_one_content_only_entry_point() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    points = project["entry-points"]
    assert points == {GROUP: {project["name"]: "universal_skills"}}
    assert any(
        d.startswith("scion-sdk") and ">=0.5.6,<0.6.0" in d
        for d in project["dependencies"]
    )


@pytest.mark.spec("US-CONTENT-R001.2")
def test_every_skill_is_flat_and_named_by_folder() -> None:
    folders = _folders()
    assert folders
    for folder in folders:
        head = (folder / "SKILL.md").read_text(encoding="utf-8").split("\n---", 1)[0]
        found = re.search(r"^name:\s*['\"]?([^'\"\n]+)", head, re.M)
        assert found and found.group(1).strip() == folder.name, folder.name


@pytest.mark.spec("US-CONTENT-R001.3")
def test_server_lists_every_skill() -> None:
    from agent_connector_sdk.connector import build_server
    from fastmcp import Client

    _, mcp = build_server("universal_skills", command_args=["--transport", "stdio"])

    async def listed() -> set[str]:
        async with Client(mcp) as client:
            uris = [str(r.uri) for r in await client.list_resources()]
        return {
            u.removeprefix("skill://").split("/", 1)[0]
            for u in uris
            if u.endswith("/SKILL.md")
        }

    assert asyncio.run(listed()) == {f.name for f in _folders()}
