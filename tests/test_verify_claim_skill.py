"""The verify-claim skill (US-CONTENT-R008)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

SKILL = Path(__file__).resolve().parent.parent / "universal_skills" / "skills" / "verify-claim" / "SKILL.md"


@pytest.mark.spec("US-CONTENT-R008")
def test_skill_states_the_loop_in_order_and_is_neutral() -> None:
    _, head, body = SKILL.read_text(encoding="utf-8").split("---", 2)
    meta = yaml.safe_load(head)
    assert meta["name"] == "verify-claim"
    assert len(meta["description"]) <= 1024
    steps = [
        body.index("`Propose`"),
        body.index("`lean_check`"),
        body.index("`RecordEvidence`"),
        body.index("`formalizes`"),
        body.index("`Get`"),
    ]
    assert steps == sorted(steps)
    assert "`fleet.call`" in body and "`lean-mcp`" in body
    assert "`has_sorry` true or verdict `fail`" in body
    assert not re.search(r"\.arpa\b|\.lan\b|\.internal\b|/home/|/Users/|/var/tmp|https?://", body)
