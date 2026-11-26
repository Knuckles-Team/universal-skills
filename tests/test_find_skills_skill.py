"""US-CONTENT-R013: the find-skills skill."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _skill_helpers import PRIVATE, in_order, lint_clean, read  # noqa: E402


@pytest.mark.spec("US-CONTENT-R013.1")
def test_steps_in_order_and_cohort_rule() -> None:
    _, body = read("find-skills")
    assert in_order(body, "Describe the task in one sentence", "`skills.find`", "quality score and the eval count", "`skills.peers.recommend`", "at most five skills")
    assert "Prefer a skill with eval runs over a skill without eval runs" in body
    assert "`PEER_COHORT_TOO_SMALL` answer means no peer list exists" in body
    assert "| Failure | Cause | Recovery |" in body and "install command" in body


@pytest.mark.spec("US-CONTENT-R013.2")
def test_registration_and_linters() -> None:
    meta, body = read("find-skills")
    assert meta["name"] == "find-skills" and meta["metadata"]["tier"] == "core"
    assert not PRIVATE.search(body)
    lint_clean("find-skills")


@pytest.mark.spec("US-CONTENT-R013")
def test_find_skills_journey() -> None:
    meta, body = read("find-skills")
    assert "installs nothing" in meta["description"] or "never installs" in body
