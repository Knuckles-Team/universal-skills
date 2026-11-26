"""US-CONTENT-R012: the always-on knowledge-flag and skill-friction skills."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _skill_helpers import PRIVATE, SKILLS, in_order, lint_clean, read  # noqa: E402

ALWAYS_ON_MAX = 100  # engine bound `skills.always_on_max` default


@pytest.mark.spec("US-CONTENT-R012.1")
def test_flag_skill_states_the_steps_and_the_curator_rule() -> None:
    _, body = read("knowledge-flag")
    assert in_order(body, "Notice a missing or wrong fact", "`knowledge.flag.list`", "`knowledge.flag.raise`", "Continue the task", "Report the flag id")
    assert "never edits knowledge" in body and "Only the curator changes it" in body
    for code in ("FLAG_TARGET_UNKNOWN", "FLAG_RUN_UNKNOWN", "FLAG_TEXT_TOO_LARGE", "FLAG_RUN_QUOTA_EXCEEDED", "FLAG_RESOLVE_ROLE_REQUIRED", "FLAG_STATE_ILLEGAL"):
        assert f"`{code}`" in body
    assert (SKILLS / "knowledge-flag" / "skill.spec.yml").is_file()


@pytest.mark.spec("US-CONTENT-R012.2")
def test_friction_skill_states_the_steps() -> None:
    _, body = read("skill-friction")
    assert in_order(body, "what you tried, what you expected and what happened", "Add the fix", "`skills.friction.report`", "Continue the task")
    assert "One report holds one friction" in body and "never blocks the task" in body
    for code in ("FRICTION_SKILL_UNKNOWN", "FRICTION_TRANSITION_ILLEGAL", "FRICTION_EVIDENCE_REQUIRED", "FRICTION_APPROVAL_ROLE_REQUIRED", "FRICTION_TEXT_TOO_LARGE"):
        assert f"`{code}`" in body
    assert (SKILLS / "skill-friction" / "skill.spec.yml").is_file()


@pytest.mark.spec("US-CONTENT-R012.3")
def test_registration_neutral_text_and_always_on_count() -> None:
    for name in ("knowledge-flag", "skill-friction"):
        meta, body = read(name)
        assert meta["name"] == name
        assert meta["metadata"]["domain"] == "development"
        assert meta["metadata"]["skill_type"] == "skill"
        assert meta["metadata"]["tier"] == "always-on"
        assert not PRIVATE.search(body)
        assert (SKILLS / name / "SKILL.md").is_file()
    tiers = [
        (read(p.parent.name)[0].get("metadata") or {}).get("tier")
        for p in SKILLS.glob("*/SKILL.md")
        if "tier:" in p.read_text(encoding="utf-8").split("---", 2)[1]
    ]
    assert 2 <= tiers.count("always-on") <= ALWAYS_ON_MAX


@pytest.mark.spec("US-CONTENT-R012")
def test_always_on_skills_journey() -> None:
    lint_clean("knowledge-flag")
    lint_clean("skill-friction")
