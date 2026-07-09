#!/usr/bin/env python3
"""Per-agent SKILL.md frontmatter adapter (cross-agent skill portability).

``install.py`` installs a skill by copying its ``SKILL.md`` VERBATIM. That is fine
for Claude-family tools (Claude Code, Windsurf, OpenClaw, Antigravity, Devin,
Cursor, Grok, OpenCode, Zed, agent-utilities) which accept our full frontmatter —
but Codex's ``~/.codex/skills`` rejects top-level keys it doesn't know about
(``tags``, ``categories``, ``domain``, ``requires``, ``tier``, ``wraps``,
``concept``, ``team_config``, ``agent``, ``cron``, ``skill_type``, ``aliases``,
``source_url``, …) and ``<``/``>`` inside ``description``.

This module defines a per-target :class:`AgentContract` describing what a target
tool's frontmatter accepts, and adapts a skill's ``SKILL.md`` **at install time**.
The canonical source stays Claude-native and is never rewritten in place — only
the installed COPY for a non-permissive target is transformed.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is a light, near-universal dep
    yaml = None

logger = logging.getLogger(__name__)


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Return ``(frontmatter_text, body)``; ``("", text)`` if no frontmatter block.

    Same tiny algorithm as ``scripts/check_atomicity.py``'s ``_split_frontmatter``.
    Duplicated rather than imported: ``scripts/`` is dev-only tooling for this repo
    and is not shipped inside the installed ``universal_skills`` package, so code
    that must work at install time (this module) cannot depend on it.
    """
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[1], parts[2]
    return "", text


@dataclass
class AgentContract:
    """What a target agent tool's ``SKILL.md`` frontmatter accepts."""

    allowed_top_level: set = field(default_factory=set)
    demote_to_metadata: bool = True
    sanitize_description: bool = True
    flat_discovery: bool = False
    builtin_skills: frozenset = frozenset()
    rename_map: dict = field(default_factory=dict)

    @property
    def requires_transform(self) -> bool:
        """True if installing under this contract needs a rewritten SKILL.md."""
        return bool(
            self.demote_to_metadata
            or self.sanitize_description
            or self.flat_discovery
            or self.rename_map
        )


# A contract with every flag off is a no-op: verbatim copy/symlink, today's behavior.
_PERMISSIVE = AgentContract(
    allowed_top_level=set(),
    demote_to_metadata=False,
    sanitize_description=False,
    flat_discovery=False,
)

# Every OTHER tool key in install.py's get_tool_paths() is permissive — Codex is
# currently the only target with a restrictive frontmatter contract.
AGENT_CONTRACTS: dict = {
    "codex": AgentContract(
        allowed_top_level={"name", "description", "license", "allowed-tools", "metadata"},
        demote_to_metadata=True,
        sanitize_description=True,
        flat_discovery=True,
        builtin_skills=frozenset({"skill-installer"}),
        rename_map={"skill-installer": "universal-skill-installer"},
    ),
    "claude": _PERMISSIVE,
    "windsurf": _PERMISSIVE,
    "openclaw": _PERMISSIVE,
    "antigravity": _PERMISSIVE,
    "devin": _PERMISSIVE,
    "cursor": _PERMISSIVE,
    "grok": _PERMISSIVE,
    "grok-code": _PERMISSIVE,
    "opencode": _PERMISSIVE,
    "zed": _PERMISSIVE,
    "agent-utilities": _PERMISSIVE,
    "agent-terminal-ui": _PERMISSIVE,
}


def get_contract(tool_key: str) -> AgentContract:
    """Resolve the contract for ``tool_key``.

    Tolerant of case and of decorated labels like ``"agent-utilities (xdg)"`` (the
    label ``install.py`` uses for the always-synced XDG target). Anything unknown —
    a custom ``--path`` target, a future tool — defaults to permissive, i.e. no
    behavior change from before this module existed.
    """
    if not tool_key:
        return _PERMISSIVE
    key = tool_key.strip().lower()
    if key in AGENT_CONTRACTS:
        return AGENT_CONTRACTS[key]
    base = re.sub(r"\s*\([^)]*\)\s*$", "", key).strip()
    return AGENT_CONTRACTS.get(base, _PERMISSIVE)


def resolve_dest_name(name: str, contract: AgentContract) -> str:
    """Return the on-disk name a skill should install as under ``contract``."""
    return contract.rename_map.get(name, name)


# Bundled-asset subtrees never count as a promotable nested sub-skill.
_ASSET_DIRS = {"assets", "resources", "references", "scripts"}


def iter_promotable_nested(skill_src: Path) -> list:
    """Nested dirs (depth >= 2 below ``skill_src``) that contain their own
    ``SKILL.md`` and are not inside an assets/resources/references/scripts
    subtree — genuine sub-skills bundled inside a parent skill, promotable to a
    flat-discovery agent's top level (e.g. Codex, which has no nested lookup).
    """
    out: list = []
    if not skill_src.is_dir():
        return out
    for skill_md in sorted(skill_src.rglob("SKILL.md")):
        nested = skill_md.parent
        if nested == skill_src:
            continue
        rel_parts = nested.relative_to(skill_src).parts
        if len(rel_parts) < 2:
            continue
        if _ASSET_DIRS.intersection(rel_parts):
            continue
        out.append(nested)
    return out


def transform_frontmatter(text: str, contract: AgentContract) -> str:
    """Adapt a SKILL.md's frontmatter to ``contract``; body is preserved byte-for-byte.

    Returns ``text`` unchanged when it has no frontmatter block, when the contract
    needs no transform (permissive — today's verbatim behavior), when PyYAML is
    unavailable, or when the frontmatter fails to parse (fails safe: verbatim copy
    beats a broken install).
    """
    if not contract.requires_transform:
        return text
    fm_text, body = _split_frontmatter(text)
    if body is text:  # no frontmatter block found
        return text
    if yaml is None:
        logger.warning(
            "PyYAML unavailable; cannot transform SKILL.md frontmatter — installing verbatim."
        )
        return text
    try:
        data = yaml.safe_load(fm_text) or {}
    except Exception as e:  # noqa: BLE001
        logger.warning("Could not parse SKILL.md frontmatter for transform: %s", e)
        return text
    if not isinstance(data, dict):
        return text

    if contract.demote_to_metadata:
        kept: dict = {}
        overflow: dict = {}
        for k, v in data.items():
            if k in contract.allowed_top_level or k == "metadata":
                kept[k] = v
            else:
                overflow[k] = v
        metadata = kept.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        for k, v in overflow.items():
            metadata.setdefault(k, v)  # existing metadata sub-keys win on conflict
        if metadata:
            kept["metadata"] = metadata
        data = kept

    if contract.sanitize_description and data.get("description"):
        data["description"] = str(data["description"]).replace("<", "[").replace(">", "]")

    dumped = yaml.safe_dump(
        data, sort_keys=False, allow_unicode=True, default_flow_style=False
    )
    # `body` (from `_split_frontmatter`) already carries its own leading newline —
    # the same boundary the original file had right after its closing `---` — so no
    # extra separator is added here (that would double the blank line).
    return f"---\n{dumped}---{body}"
