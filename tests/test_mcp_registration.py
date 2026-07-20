"""Current MCP registration contracts shared with agent-utilities."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1])


def test_codex_is_not_a_json_config_target() -> None:
    installer = _load(
        "test_mcp_installer",
        ROOT
        / "universal_skills"
        / "agent-tools"
        / "mcp-installer"
        / "scripts"
        / "install.py",
    )

    assert "codex" not in installer.TOOL_PATHS
    assert all(".codex" not in str(path) for path in installer.TOOL_PATHS.values())


def test_graph_os_json_launcher_is_portable_and_contains_no_runtime_state() -> None:
    setup = _load(
        "test_mcp_setup",
        ROOT
        / "universal_skills"
        / "core"
        / "universal-installer"
        / "scripts"
        / "mcp_setup.py",
    )

    entry = setup.build_graph_os_entry()
    assert entry == {"command": "graph-os", "args": ["--transport", "stdio"]}
    encoded = json.dumps(entry)
    assert "env" not in entry
    assert "workspace" not in encoded.lower()
    assert "secret" not in encoded.lower()


def test_touched_installer_skills_keep_canonical_catalog_metadata() -> None:
    for domain, name in (
        ("agent-tools", "mcp-installer"),
        ("core", "universal-installer"),
    ):
        skill = ROOT / "universal_skills" / domain / name / "SKILL.md"
        metadata = _frontmatter(skill)
        assert metadata["name"] == name
        assert metadata["domain"] == domain
        assert metadata["skill_type"] == "skill"
        assert "Use when" in str(metadata["description"])

    mcp_skill = (
        ROOT
        / "universal_skills"
        / "agent-tools"
        / "mcp-installer"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "codex mcp add graph-os -- graph-os --transport stdio" in mcp_skill
