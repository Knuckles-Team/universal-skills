"""A copied provider skill must remain traceable to its installed source."""

from pathlib import Path

from universal_skills.core import universal_installer


def test_installed_skill_check_reports_missing_and_changed_files(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source" / "example-skill"
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text(
        "---\nname: example-skill\ndescription: Example\n---\nOriginal body\n"
    )
    (source / "reference.txt").write_text("Evidence\n")
    target = tmp_path / "codex"
    contract = universal_installer._impl.adapters.get_contract("codex")

    assert universal_installer._impl.check_skill_install(
        target, [source], contract
    ) == [f"missing: {target / 'example-skill'}"]
    assert universal_installer._impl.install_skills(
        target, sources=[source], force=True, contract=contract
    )
    assert (
        universal_installer._impl.check_skill_install(target, [source], contract) == []
    )

    (target / "example-skill" / "reference.txt").write_text("Stale\n")
    assert universal_installer._impl.check_skill_install(
        target, [source], contract
    ) == [f"changed: {target / 'example-skill' / 'reference.txt'}"]


def test_check_uses_transformed_frontmatter(tmp_path: Path) -> None:
    source = tmp_path / "source" / "skill"
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text(
        "---\nname: skill\ndescription: Example\ndomain: test\n---\nBody\n"
    )
    target = tmp_path / "codex"
    contract = universal_installer._impl.adapters.get_contract("codex")
    assert universal_installer._impl.install_skills(
        target, sources=[source], force=True, contract=contract
    )
    assert (
        universal_installer._impl.check_skill_install(target, [source], contract) == []
    )

    (source / "SKILL.md").write_text(
        "---\nname: skill\ndescription: Example\ndomain: test\n---\nNew body\n"
    )
    assert universal_installer._impl.check_skill_install(
        target, [source], contract
    ) == [f"changed: {target / 'skill' / 'SKILL.md'}"]
