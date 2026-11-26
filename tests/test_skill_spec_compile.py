"""US-CONTENT-R009: a skill spec compiles into SKILL.md, prompts and overlays."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "universal_skills" / "skills"
ALWAYS_ON = ("knowledge-flag", "skill-friction")
sys.path.insert(0, str(ROOT))

from universal_skills import skill_spec as ss  # noqa: E402

_spec = importlib.util.spec_from_file_location("compile_skill_spec", ROOT / "scripts" / "compile_skill_spec.py")
assert _spec and _spec.loader
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)

GOOD = {
    "goal": "Do one thing.",
    "outputs": ["A result."],
    "required_tool_actions": ["tool.a"],
    "forbidden_tool_actions": ["tool.b"],
    "target_agents": ["claude"],
    "target_models": ["standard-model"],
    "steps": [
        {
            "objective": "Run the check.",
            "command": "tool.a",
            "verify": "The answer is ok.",
            "on_failure": "Stop and report the error code.",
        }
    ],
}
SHELL = "---\nname: demo\ndescription: d\nmetadata:\n  version: '1'\n---\n\nIntro text.\n\n<!-- spec:begin -->\n<!-- spec:end -->\n\nTail text.\n"


def _parse(data: dict) -> ss.SkillSpec:
    return ss.parse_spec(yaml.safe_dump(data))


@pytest.mark.spec("US-CONTENT-R009.1")
def test_spec_model_refuses_unknown_keys() -> None:
    assert _parse(GOOD).goal == "Do one thing."
    with pytest.raises(ss.SpecError) as err:
        _parse({**GOOD, "extra": 1})
    assert err.value.code == ss.SPEC_UNKNOWN_KEY
    with pytest.raises(ss.SpecError):
        _parse({**GOOD, "steps": [{**GOOD["steps"][0], "other": 1}]})
    assert cs.load_spec(SKILLS / "knowledge-flag" / "skill.spec.yml").steps


@pytest.mark.spec("US-CONTENT-R009.2")
def test_compile_is_deterministic_and_keeps_outside_text() -> None:
    spec = _parse(GOOD)
    one = ss.compile_skill(spec, "demo", SHELL)
    two = ss.compile_skill(spec, "demo", SHELL)
    assert one == two
    assert one.skill_md.startswith("---\nname: demo")
    assert "Intro text." in one.skill_md and one.skill_md.endswith("Tail text.\n")
    assert "1. Run the check." in one.skill_md and "| Failure | Cause | Recovery |" in one.skill_md
    rows = [json.loads(x) for x in one.prompts_jsonl.splitlines()]
    assert len(rows) == 2
    assert rows[0]["expected_trajectory"][-1] == {"kind": "tool", "name": "tool.a"}
    assert rows[1]["forbidden"] == [{"kind": "tool", "name": "tool.b"}]
    assert ss.compile_skill(spec, "demo", one.skill_md).skill_md == one.skill_md


@pytest.mark.spec("US-CONTENT-R009.3")
def test_check_names_stale_skills_after_a_model_change(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    skills, overlays = tmp_path / "skills", tmp_path / "overlays"
    folder = skills / "demo"
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(SHELL)
    (folder / "skill.spec.yml").write_text(yaml.safe_dump(GOOD))
    targets = tmp_path / "targets.yml"
    targets.write_text(yaml.safe_dump({"agents": ["claude"], "models": ["standard-model"]}))
    base = ["--skills", str(skills), "--overlays", str(overlays), "--targets", str(targets)]
    assert cs.main(base) == 0
    assert (overlays / "demo" / "standard-model.md").read_text().startswith("---\nmode: append\n---")
    assert cs.main(["--check", *base]) == 0
    (folder / "SKILL.md").write_text((folder / "SKILL.md").read_text().replace("Run the check.", "Edited."))
    assert cs.main(["--check", *base]) == 1
    assert "SKILL_COMPILE_STALE: demo" in capsys.readouterr().out
    assert cs.main(base) == 0
    targets.write_text(yaml.safe_dump({"agents": ["claude"], "models": ["other-model"]}))
    assert cs.main(["--check", *base]) == 1
    assert "SPEC_TARGET_UNKNOWN" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("change", "code"),
    [
        ({"steps": [{**GOOD["steps"][0], "verify": ""}]}, ss.SPEC_STEP_INCOMPLETE),
        ({"steps": [{**GOOD["steps"][0], "command": " "}]}, ss.SPEC_STEP_INCOMPLETE),
        ({"forbidden_tool_actions": ["tool.a"]}, ss.SPEC_TOOL_CONFLICT),
        ({"target_models": ["no-such-model"]}, ss.SPEC_TARGET_UNKNOWN),
        ({"target_agents": ["no-such-agent"]}, ss.SPEC_TARGET_UNKNOWN),
        ({"steps": [{**GOOD["steps"][0], "on_failure": "Retry."}]}, ss.SPEC_RECOVERY_VAGUE),
        ({"steps": [{**GOOD["steps"][0], "on_failure": "Try again"}]}, ss.SPEC_RECOVERY_VAGUE),
    ],
)
@pytest.mark.spec("US-CONTENT-R009.4")
def test_each_refusal_code_writes_nothing(change: dict, code: str, tmp_path: Path) -> None:
    folder = tmp_path / "skills" / "demo"
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(SHELL)
    (folder / "skill.spec.yml").write_text(yaml.safe_dump({**GOOD, **change}))
    with pytest.raises(ss.SpecError) as err:
        _parse({**GOOD, **change})
    assert err.value.code == code
    assert cs.main(["--skills", str(tmp_path / "skills"), "--overlays", str(tmp_path / "ov")]) == 1
    assert (folder / "SKILL.md").read_text() == SHELL
    assert not (folder / "evals").exists() and not (tmp_path / "ov").exists()


@pytest.mark.spec("US-CONTENT-R009.5")
def test_digest_binds_the_spec() -> None:
    first = ss.compile_skill(_parse(GOOD), "demo", SHELL).skill_md
    changed = _parse({**GOOD, "goal": "Do another thing."})
    second = ss.compile_skill(changed, "demo", SHELL).skill_md
    assert f"spec_digest: '{_parse(GOOD).digest}'" in first
    assert first != second and _parse(GOOD).digest != changed.digest


@pytest.mark.spec("US-CONTENT-R009.6")
def test_always_on_skills_compile_to_the_committed_files(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cs.main(["--check"]) == 0
    for name in ALWAYS_ON:
        assert (SKILLS / name / "evals" / "prompts.jsonl").is_file()
    config = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text())
    hooks = {h["id"]: h for repo in config["repos"] for h in repo["hooks"]}
    assert hooks["compile-skill-spec"]["entry"].endswith("compile_skill_spec.py --check")
    narrowed = tmp_path / "targets.yml"
    narrowed.write_text(yaml.safe_dump({"agents": ["arbora", "claude", "codex"], "models": ["standard-model"]}))
    assert cs.main(["--check", "--targets", str(narrowed)]) == 1
    out = capsys.readouterr().out
    assert "knowledge-flag" in out and "skill-friction" in out


@pytest.mark.spec("US-CONTENT-R009")
def test_compile_journey() -> None:
    spec = cs.load_spec(SKILLS / "find-skills" / "skill.spec.yml")
    text = (SKILLS / "find-skills" / "SKILL.md").read_text()
    assert ss.compile_skill(spec, "find-skills", text).skill_md == text
