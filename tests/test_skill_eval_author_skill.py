"""US-CONTENT-R015: the skill-eval-author skill."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _skill_helpers import PRIVATE, in_order, lint_clean, read  # noqa: E402


@pytest.mark.spec("US-CONTENT-R015.1")
def test_steps_band_rules_and_codes() -> None:
    _, body = read("skill-eval-author")
    assert in_order(body, "Add one golden case with tool mocks", "Add real prompts from traces", "Add author-judged cases last", "`skills.eval.run`")
    assert "between 70 and 90 percent is healthy" in body and "100 percent is suspicious" in body
    assert "Outcome and trajectory are separate scores" in body
    assert "calibration run against an annotated set" in body
    assert "inside the noise band is no effect" in body
    for code in ("JUDGE_NOT_CALIBRATED", "EVAL_RUN_NOT_CLEAN_ROOM", "EVAL_CASE_INVALID", "ABLATION_WITHIN_NOISE", "ABLATION_NOISE_BAND_MISSING", "COMPILE_MODEL_UNKNOWN"):
        assert f"`{code}`" in body


@pytest.mark.spec("US-CONTENT-R015.2")
def test_registration_and_linters() -> None:
    meta, body = read("skill-eval-author")
    assert meta["metadata"]["tier"] == "core" and not PRIVATE.search(body)
    lint_clean("skill-eval-author")


@pytest.mark.spec("US-CONTENT-R015")
def test_eval_author_journey() -> None:
    meta, _ = read("skill-eval-author")
    assert meta["name"] == "skill-eval-author"
