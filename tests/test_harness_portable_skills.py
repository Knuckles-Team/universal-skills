"""Catalog content for the arbora harness bundle (US-CONTENT-R007.2 to R007.4)."""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "universal_skills" / "skills"
INSTALLER = SKILLS / "universal-installer" / "scripts" / "install.py"
PORTABLE_KEYS = {"name", "description", "license", "metadata", "allowed-tools", "compatibility"}


def _frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    _, head, body = text.split("---", 2)
    return yaml.safe_load(head), body


def _portable(meta: dict, folder: str) -> None:
    assert meta["name"] == folder
    assert re.fullmatch(r"[a-z0-9-]{1,64}", meta["name"])
    assert isinstance(meta["description"], str) and len(meta["description"]) <= 1024
    assert set(meta) <= PORTABLE_KEYS


@pytest.mark.spec("US-CONTENT-R007.2")
def test_door_skill_states_the_rules_and_is_neutral() -> None:
    meta, body = _frontmatter(SKILLS / "canopy" / "SKILL.md")
    _portable(meta, "canopy")
    for tool in ("find", "ask", "why", "write", "act", "manage"):
        assert f"`{tool}`" in body
    rules = [
        body.index("Discover before concluding"),
        body.index("Preview a write, then resubmit"),
        body.index("`fleet.call`"),
        body.index("`agents.run`"),
    ]
    assert rules == sorted(rules)
    assert "plan_ref" in body
    assert "arbora plugin statusline" in body
    assert not re.search(r"\.arpa\b|\.lan\b|\.internal\b|/home/|/Users/|/var/tmp|https?://", body)


@pytest.mark.spec("US-CONTENT-R007.3")
def test_handoff_skill_states_the_workstream_path_first() -> None:
    meta, body = _frontmatter(SKILLS / "session-handoff" / "SKILL.md")
    _portable(meta, "session-handoff")
    first = body.index("## ")
    assert body[first:].startswith("## The workstream path first")
    section = body[first : body.index("## ", first + 3)]
    assert 'op="workstream.checkpoint"' in section and "2000 characters or fewer" in section
    assert 'op="workstream.get"' in section
    assert "only when the door is unreachable" in section
    assert section.index("workstream.checkpoint") < body.index("create_handoff.py")


def _installer():
    spec = importlib.util.spec_from_file_location("us_installer", str(INSTALLER))
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(INSTALLER.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


@pytest.mark.spec("US-CONTENT-R007.4")
def test_installer_refuses_bundle_profiles_and_writes_nothing(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    env = {**os.environ, "HOME": str(home), "XDG_CONFIG_HOME": str(home / ".config")}
    for tool, profile in (
        ("claude", "claude-code"),
        ("opencode", "opencode"),
        ("codex", "codex"),
        ("grok", "grok"),
        ("grok-code", "grok"),
    ):
        done = subprocess.run(
            [sys.executable, str(INSTALLER), "--tool", tool, "--no-xdg"],
            capture_output=True,
            text=True,
            env=env,
            timeout=120,
            stdin=subprocess.DEVNULL,
        )
        assert done.returncode == 2, done.stderr
        assert f"arbora plugin install --harness {profile}" in done.stderr
        assert [p for p in home.rglob("*")] == []
    module = _installer()
    kept = module.drop_bundle_profiles(dict(module.TOOL_PATHS))
    assert not set(kept) & set(module.BUNDLE_PROFILES)
    assert set(module.TOOL_PATHS) - set(module.BUNDLE_PROFILES) == set(kept)
    sys.path.insert(0, str(INSTALLER.parent))
    try:
        import mcp_setup
    finally:
        sys.path.pop(0)
    assert not set(mcp_setup.MCP_CONFIG_PATHS) & set(module.BUNDLE_PROFILES)


@pytest.mark.spec("US-CONTENT-R007.4")
def test_install_removes_renamed_skills(tmp_path: Path) -> None:
    import json

    module = _installer()
    mapping = json.loads((SKILLS / "renamed-skills.json").read_text(encoding="utf-8"))["renamed"]
    assert mapping and all(old != new for old, new in mapping.items())
    for successor in filter(None, mapping.values()):
        assert (SKILLS / successor / "SKILL.md").is_file(), successor
    assert not set(mapping) & {p.name for p in SKILLS.iterdir()}
    target = tmp_path / "skills"
    target.mkdir()
    (target / "epistemic-graph-development").mkdir()
    (target / "epistemic-graph-development" / "SKILL.md").write_text("old", encoding="utf-8")
    (target / "using-graph-os").symlink_to(tmp_path)
    (target / "kept-skill").mkdir()
    removed = module.prune_renamed_skills(target, {"medulla-development"})
    assert removed == ["epistemic-graph-development", "using-graph-os"]
    assert sorted(p.name for p in target.iterdir()) == ["kept-skill"]
    (target / "old-a").mkdir()
    assert module.prune_renamed_skills(target, {"old-a"}, {"old-a": "new-a"}) == []
    assert (target / "old-a").is_dir()
