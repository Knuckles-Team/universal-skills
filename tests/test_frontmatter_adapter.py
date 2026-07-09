"""Tests for the per-agent SKILL.md frontmatter adapter (adapters.py).

Loaded by file path (like test_mcp_client_onboarder.py) since its containing
directory is hyphenated (``core/skill-installer/scripts/``) and cannot be
`import`ed by a normal dotted path.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

SCRIPTS = Path(__file__).resolve().parent.parent / (
    "universal_skills/core/skill-installer/scripts"
)


def _mod(name):
    spec = importlib.util.spec_from_file_location(name, str(SCRIPTS / f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m  # dataclasses needs the module registered to resolve types
    spec.loader.exec_module(m)
    return m


adapters = _mod("adapters")


CODEX = adapters.AGENT_CONTRACTS["codex"]
CLAUDE = adapters.AGENT_CONTRACTS["claude"]


SAMPLE_SKILL_MD = """---
name: sample-skill
domain: finance
skill_type: skill
description: >-
  Does <a thing> for the agent. Use when >needed<.
tags: [finance, sample]
requires: [other-skill]
license: MIT
metadata:
  version: '1.0.0'
  author: Genius
---
# Sample Skill

Body content here, unchanged by any transform.
"""


def test_demote_moves_non_allowed_keys_without_clobbering_metadata():
    out = adapters.transform_frontmatter(SAMPLE_SKILL_MD, CODEX)
    fm_text, body = adapters._split_frontmatter(out)
    data = yaml.safe_load(fm_text)

    # Only Codex-allowed top-level keys remain.
    assert set(data.keys()) <= CODEX.allowed_top_level

    # Demoted keys land under metadata, existing metadata sub-keys untouched.
    assert data["metadata"]["version"] == "1.0.0"
    assert data["metadata"]["author"] == "Genius"
    assert data["metadata"]["domain"] == "finance"
    assert data["metadata"]["skill_type"] == "skill"
    assert data["metadata"]["tags"] == ["finance", "sample"]
    assert data["metadata"]["requires"] == ["other-skill"]

    # Body is preserved byte-for-byte.
    assert body == SAMPLE_SKILL_MD.split("---", 2)[2]


def test_demote_does_not_overwrite_existing_metadata_subkey():
    text = """---
name: x
domain: core
description: d
metadata:
  domain: keep-me
---
body
"""
    out = adapters.transform_frontmatter(text, CODEX)
    data = yaml.safe_load(adapters._split_frontmatter(out)[0])
    # `domain` already existed inside metadata -> it must win over the demoted
    # top-level `domain: core`.
    assert data["metadata"]["domain"] == "keep-me"


def test_description_sanitization_strips_angle_brackets():
    out = adapters.transform_frontmatter(SAMPLE_SKILL_MD, CODEX)
    data = yaml.safe_load(adapters._split_frontmatter(out)[0])
    assert "<" not in data["description"]
    assert ">" not in data["description"]
    assert "[a thing]" in data["description"]


def test_rename_map_applies_to_skill_installer():
    assert adapters.resolve_dest_name("skill-installer", CODEX) == "universal-skill-installer"
    assert adapters.resolve_dest_name("web-search", CODEX) == "web-search"


def test_permissive_contract_is_a_noop():
    assert CLAUDE.requires_transform is False
    out = adapters.transform_frontmatter(SAMPLE_SKILL_MD, CLAUDE)
    assert out == SAMPLE_SKILL_MD
    assert adapters.resolve_dest_name("skill-installer", CLAUDE) == "skill-installer"


def test_transform_is_noop_without_frontmatter():
    text = "# No frontmatter here\n\nJust a body.\n"
    assert adapters.transform_frontmatter(text, CODEX) == text


def test_get_contract_tolerant_of_case_and_labels():
    assert adapters.get_contract("CODEX") is CODEX
    assert adapters.get_contract("agent-utilities (xdg)") is adapters.AGENT_CONTRACTS[
        "agent-utilities"
    ]
    assert adapters.get_contract("/some/custom/path").requires_transform is False
    assert adapters.get_contract("").requires_transform is False


def test_iter_promotable_nested_finds_subskills_and_excludes_assets(tmp_path):
    skill_src = tmp_path / "parent-skill"
    # A genuine bundled sub-skill: depth 2 below skill_src.
    (skill_src / "bundled" / "sub-one").mkdir(parents=True)
    (skill_src / "bundled" / "sub-one" / "SKILL.md").write_text("---\nname: sub-one\n---\n")

    (skill_src / "assets" / "bundled-thing").mkdir(parents=True)
    (skill_src / "assets" / "bundled-thing" / "SKILL.md").write_text(
        "---\nname: bundled-thing\n---\n"
    )

    (skill_src / "scripts" / "helper-skill").mkdir(parents=True)
    (skill_src / "scripts" / "helper-skill" / "SKILL.md").write_text(
        "---\nname: helper-skill\n---\n"
    )

    # top-level SKILL.md itself must not be treated as "nested".
    (skill_src / "SKILL.md").write_text("---\nname: parent-skill\n---\n")

    nested = adapters.iter_promotable_nested(skill_src)
    names = {p.name for p in nested}
    assert names == {"sub-one"}


def test_iter_promotable_nested_empty_for_nonexistent_dir(tmp_path):
    assert adapters.iter_promotable_nested(tmp_path / "does-not-exist") == []
