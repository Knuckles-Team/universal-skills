"""US-CONTENT-R001.5: the connector standard reads this package as a content-only connector."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
SCHEMAS = "universal_skills/skills/document-tools/scripts/{}_scripts/office/schemas"

pytestmark = pytest.mark.spec("US-CONTENT-R001.5")


def test_declares_the_content_only_profile_and_its_vendored_content() -> None:
    table = PYPROJECT["tool"]["pipelines"]["connector"]
    assert set(table) == {"profile", "vendored"}
    assert table["profile"] == "content-only"
    expected = ["universal_skills/upstream", *(SCHEMAS.format(kind) for kind in ("docx", "pptx", "xlsx"))]
    assert table["vendored"] == expected
    for path in table["vendored"]:
        assert (ROOT / path).is_dir(), path
        assert path != "universal_skills" and not "universal_skills".startswith(path + "/")


def test_rendered_upstream_skills_keep_their_wording_out_of_codespell() -> None:
    upstream = tomllib.loads((ROOT / "upstream-sources.toml").read_text(encoding="utf-8"))
    rendered = {
        f"universal_skills/skills/{skill['name']}"
        for source in upstream["source"]
        if source.get("transform") == "skill-md"
        for skill in source.get("skill", [])
    }
    assert set(PYPROJECT["tool"]["pipelines"]["codespell"]["exclude"]) == rendered
