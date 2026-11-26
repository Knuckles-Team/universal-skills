"""US-CONTENT-R011: skill stage budgets and key placement."""

from __future__ import annotations

import importlib.util
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "universal_skills" / "skills"
NEW = ("knowledge-flag", "skill-friction", "find-skills", "knowledge-curator", "skill-eval-author")

_spec = importlib.util.spec_from_file_location("check_skill_budgets", ROOT / "scripts" / "check_skill_budgets.py")
assert _spec and _spec.loader
ckb = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = ckb
_spec.loader.exec_module(ckb)


def _make(tmp: Path, fm: str = "", body: str = "Body.\n") -> Path:
    folder = tmp / "demo"
    folder.mkdir()
    (folder / "SKILL.md").write_text(f"---\nname: demo\ndescription: short\n{fm}---\n{body}")
    return folder


def _codes(folder: Path) -> list[str]:
    return [f.code for f in ckb.lint_folder(folder)]


@pytest.mark.spec("US-CONTENT-R011.1")
def test_each_budget_code_fires_once(tmp_path: Path) -> None:
    folder = tmp_path / "demo"
    folder.mkdir()
    long_desc = "x" * 401
    (folder / "SKILL.md").write_text(
        f"---\nname: demo\ndescription: {long_desc}\n---\n" + "line\n" * 501 + "[doc](notes.md)\n"
    )
    (folder / "notes.md").write_text("n")
    assert sorted(_codes(folder)) == ["BODY_TOO_LONG", "DESCRIPTION_TOO_LONG", "REFERENCE_NOT_STAGED"]
    (folder / "SKILL.md").write_text("---\nname: demo\ndescription: ok\n---\n[doc](references/notes.md)\n")
    (folder / "references").mkdir()
    (folder / "references" / "notes.md").write_text("n")
    assert _codes(folder) == []


@pytest.mark.spec("US-CONTENT-R011.2")
def test_new_keys_live_under_metadata_only(tmp_path: Path) -> None:
    ok = _make(tmp_path, "metadata:\n  tier: core\n  owner_team: t\n  personas: [a]\n")
    assert _codes(ok) == []
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "SKILL.md").write_text("---\nname: bad\ndescription: d\ntier: core\n---\nb\n")
    assert _codes(bad) == ["KEY_NOT_IN_METADATA"]
    odd = tmp_path / "odd"
    odd.mkdir()
    (odd / "SKILL.md").write_text("---\nname: odd\ndescription: d\nmetadata:\n  tier: huge\n  load_script: scripts/run.sh\n---\nb\n")
    assert sorted(_codes(odd)) == ["LOAD_SCRIPT_MISSING", "TIER_INVALID"]
    (odd / "scripts").mkdir()
    (odd / "scripts" / "run.sh").write_text("curl https://example.com\n")
    assert "LOAD_SCRIPT_NETWORK" in _codes(odd)
    (odd / "scripts" / "run.sh").write_text("echo local\n")
    assert "LOAD_SCRIPT_NETWORK" not in _codes(odd) and "LOAD_SCRIPT_MISSING" not in _codes(odd)


@pytest.mark.spec("US-CONTENT-R011.3")
def test_mcp_json_in_a_skill_fails(tmp_path: Path) -> None:
    folder = _make(tmp_path)
    (folder / ".mcp.json").write_text("{}")
    assert _codes(folder) == ["SKILL_HAS_CONNECTOR_FILE"]
    (folder / ".mcp.json").unlink()
    (folder / "cfg.json").write_text('{"mcpServers": {}}')
    assert _codes(folder) == ["SKILL_HAS_CONNECTOR_FILE"]


@pytest.mark.spec("US-CONTENT-R011.4")
def test_new_skills_are_within_budget() -> None:
    report: Counter[str] = Counter()
    for folder in sorted(p.parent for p in SKILLS.glob("*/SKILL.md")):
        findings = ckb.lint_folder(folder)
        report.update(f.code for f in findings)
        if folder.name in NEW:
            assert findings == [], folder.name
    assert set(report) <= {
        "DESCRIPTION_TOO_LONG", "BODY_TOO_LONG", "REFERENCE_NOT_STAGED", "SKILL_HAS_CONNECTOR_FILE",
        "KEY_NOT_IN_METADATA", "TIER_INVALID", "LOAD_SCRIPT_MISSING", "LOAD_SCRIPT_NETWORK",
    }


@pytest.mark.spec("US-CONTENT-R011")
def test_budget_journey(capsys: pytest.CaptureFixture[str]) -> None:
    assert ckb.main([str(SKILLS / n) for n in NEW]) == 0
    assert capsys.readouterr().out == ""
