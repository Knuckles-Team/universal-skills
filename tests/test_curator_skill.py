"""US-CONTENT-R014: the knowledge-curator skill."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _skill_helpers import PRIVATE, ROOT, SKILLS, in_order, lint_clean, read  # noqa: E402


@pytest.mark.spec("US-CONTENT-R014.1")
def test_steps_codes_and_prohibitions() -> None:
    _, body = read("knowledge-curator")
    assert in_order(body, "`knowledge.curation.inputs`", "Group the flags by target", "Read the linked traces and the raw source", "Decide the smallest edit", "`knowledge.curation.propose`", "Stop when every flag has a proposal")
    for code in ("CONTRADICTS_ACTIVE_DEFINITION", "CONTRADICTS_INVARIANT", "REFERENCE_UNRESOLVED", "UPDATE_BASE_STALE"):
        assert f"`{code}`" in body
    assert "Never edit a skill or an entry directly" in body
    assert "no flag and no source change supports" in body
    assert "report state `ready`" in body


@pytest.mark.spec("US-CONTENT-R014.2")
def test_data_access_section_names_source_query_and_columns() -> None:
    _, body = read("knowledge-curator")
    section = body.split("## Data-access entries", 1)[1].split("##", 1)[0]
    assert "`DataAccess`" in section
    assert "source that holds a fact" in section and "query that reads it" in section and "column names" in section
    assert "source schema" in section and "rename" in section and "`REFERENCE_UNRESOLVED`" in section


@pytest.mark.spec("US-CONTENT-R014.3")
def test_registration_and_compile() -> None:
    meta, body = read("knowledge-curator")
    assert meta["metadata"]["tier"] == "core" and not PRIVATE.search(body)
    lint_clean("knowledge-curator")
    sys.path.insert(0, str(ROOT))
    from universal_skills import skill_spec as ss

    spec = ss.parse_spec((SKILLS / "knowledge-curator" / "skill.spec.yml").read_text())
    text = (SKILLS / "knowledge-curator" / "SKILL.md").read_text()
    assert ss.compile_skill(spec, "knowledge-curator", text).skill_md == text


@pytest.mark.spec("US-CONTENT-R014")
def test_curator_journey() -> None:
    meta, _ = read("knowledge-curator")
    assert meta["name"] == "knowledge-curator"
