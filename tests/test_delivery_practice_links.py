"""US-CONTENT-R005: delivery skills link the delivery practice reference and name the articles."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
SKILLS = ("sdd-full-lifecycle", "sdd-implementer", "arbora-development", "medulla-development", "speckit-implement")
REFERENCE = "pipelines/blob/main/reference/delivery-practice.md"
ARTICLES = ("XVIII", "XXV", "XXVIII", "XXIX")
COPIED_TITLES = ("## Waiting and polling", "## Merge order and the hold", "## Registries keyed on spec directories")


@pytest.mark.spec("US-CONTENT-R005")
@pytest.mark.parametrize("name", SKILLS)
def test_delivery_skills_link_the_reference_and_the_articles(name: str) -> None:
    text = (ROOT / "universal_skills" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    assert REFERENCE in text, name
    for article in ARTICLES:
        assert article in text, f"{name}: {article}"
    for title in COPIED_TITLES:
        assert title not in text, f"{name} copies {title}"
