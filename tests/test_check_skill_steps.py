"""US-CONTENT-R010: the skill step and error-recovery linter."""

from __future__ import annotations

import importlib.util
import sys
import re
import sys
from collections import Counter
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "universal_skills" / "skills"
NEW = ("knowledge-flag", "skill-friction", "find-skills", "knowledge-curator", "skill-eval-author")

_spec = importlib.util.spec_from_file_location("check_skill_steps", ROOT / "scripts" / "check_skill_steps.py")
assert _spec and _spec.loader
cks = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = cks
_spec.loader.exec_module(cks)

TABLE = "\n| Failure | Cause | Recovery |\n| --- | --- | --- |\n| Step 1 fails | Bad input. | Run `fix --input` and stop. |\n"


def _skill(steps: str, table: str = TABLE) -> str:
    return f"---\nname: x\ndescription: d\n---\n\n## Steps\n\n{steps}\n{table}"


@pytest.mark.spec("US-CONTENT-R010.1")
def test_each_step_finding_has_its_code_and_line() -> None:
    good = "1. Read it.\n   - Run: `cat f`\n   - Verify: The file is not empty."
    assert cks.lint_skill(_skill(good)) == []
    two = "1. Read it and then write it.\n   - Run: `cat f`\n   - Verify: ok"
    nocmd = "1. Read it.\n   - Verify: ok"
    noverify = "1. Read it.\n   - Run: `cat f`"
    found = {
        "STEP_MULTI_OBJECTIVE": cks.lint_skill(_skill(two)),
        "STEP_NO_COMMAND": cks.lint_skill(_skill(nocmd)),
        "STEP_NO_VERIFY": cks.lint_skill(_skill(noverify)),
    }
    for code, items in found.items():
        assert [f.code for f in items] == [code]
        assert items[0].line == 8
    marked = "---\nname: x\ndescription: d\n---\n\n<!-- spec:begin -->\n1. A.\n   - Run: `a`\n   - Verify: ok\n<!-- spec:end -->\n" + TABLE
    assert cks.lint_skill(marked) == []
    assert [f.code for f in cks.lint_skill("---\nname: x\ndescription: d\n---\nNo steps.\n")] == ["STEPS_MISSING"]


@pytest.mark.spec("US-CONTENT-R010.2")
def test_vague_recovery_fails_and_concrete_recovery_passes() -> None:
    step = "1. Read it.\n   - Run: `cat f`\n   - Verify: ok"
    for vague in ("Retry.", "Try again", "Rerun the command", "retry again"):
        table = f"\n| Failure | Cause | Recovery |\n| --- | --- | --- |\n| a | b | {vague} |\n"
        assert [f.code for f in cks.lint_skill(_skill(step, table))] == ["RECOVERY_VAGUE"], vague
    assert [f.code for f in cks.lint_skill(_skill(step, ""))] == ["RECOVERY_TABLE_MISSING"]
    for concrete in ("Run `fix` first", "Use a different input and stop", "Stop with the report state `failed`"):
        table = f"\n| Failure | Cause | Recovery |\n| --- | --- | --- |\n| a | b | {concrete} |\n"
        assert cks.lint_skill(_skill(step, table)) == []


@pytest.mark.spec("US-CONTENT-R010.3")
def test_hook_entry_exists_and_runs_over_changed_skills() -> None:
    config = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text())
    hooks = {h["id"]: h for repo in config["repos"] for h in repo["hooks"]}
    hook = hooks["check-skill-steps"]
    assert hook["entry"] == "python scripts/check_skill_steps.py"
    assert hook["pass_filenames"] is True
    assert re.match(hook["files"], "universal_skills/skills/find-skills/SKILL.md")
    ids = [h["id"] for repo in config["repos"] for h in repo["hooks"]]
    assert ids.index("check-atomicity") < ids.index("check-skill-steps")
    assert "baseline" not in str(hook).lower()


@pytest.mark.spec("US-CONTENT-R010.4")
def test_exit_codes_and_line_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    folder = tmp_path / "x"
    folder.mkdir()
    (folder / "SKILL.md").write_text(_skill("1. Read it.\n   - Verify: ok"))
    assert cks.main([str(folder / "SKILL.md")]) == 1
    assert re.fullmatch(r".+SKILL\.md:8: STEP_NO_COMMAND\n", capsys.readouterr().out)
    (folder / "SKILL.md").write_text(_skill("1. Read it.\n   - Run: `cat f`\n   - Verify: ok"))
    assert cks.main([str(folder)]) == 0
    missing = tmp_path / "gone"
    missing.mkdir()
    (missing / "SKILL.md").write_bytes(b"\xff\xfe")
    assert cks.main([str(missing / "SKILL.md")]) == 2


@pytest.mark.spec("US-CONTENT-R010.5")
def test_new_knowledge_skills_pass_clean() -> None:
    counts: Counter[str] = Counter()
    for skill in sorted(SKILLS.glob("*/SKILL.md")):
        findings = cks.lint_skill(skill.read_text(encoding="utf-8"), str(skill))
        counts.update(f.code for f in findings)
        if skill.parent.name in NEW:
            assert findings == [], skill.parent.name
    assert isinstance(counts, Counter)


@pytest.mark.spec("US-CONTENT-R010")
def test_linter_journey() -> None:
    for name in NEW:
        assert cks.main([str(SKILLS / name)]) == 0
