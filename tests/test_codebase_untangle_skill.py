"""The codebase-untangle skill states its procedure, categories and gates."""

from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "universal_skills" / "skills" / "codebase-untangle" / "SKILL.md"


def test_skill_states_the_procedure_the_categories_and_the_gates() -> None:
    # spec: US-CONTENT-R006
    text = SKILL.read_text(encoding="utf-8")
    steps = [
        "Settle comments and tests first",
        "List every problem and change nothing",
        "Measure with our gates",
        "Redesign from first principles",
        "File the redesign before code",
        "Fix everything",
        "Review until clean",
    ]
    positions = [text.index(step) for step in steps]
    assert positions == sorted(positions)
    for category in ("Hidden links", "Needless links", "Surplus", "Special cases", "Custom code in environment"):
        assert category in text
    for gate in ("kiss-census", "complexity-census", "dupehound", "coupling", "state-machine-census"):
        assert gate in text
    assert "decision log" in text
