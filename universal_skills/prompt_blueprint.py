"""Canonical system-prompt blueprint contract used by the prompt-builder skill.

Pure Python, no engine or agent-runtime import. Medulla owns validation of packaged
prompts at import (``MEDULLA-DECISION-ENGINE-R814.8``); this module authors and
checks the same contract locally.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
COMPOSE_MODES = ("append", "prepend", "replace")
_SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def validate_canonical(data: Any) -> list[str]:
    """Return one ``field: rule`` message per violation; empty means conformant."""
    if not isinstance(data, dict):
        return ["$: blueprint must be an object"]
    errors: list[str] = []
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version: must be {SCHEMA_VERSION!r}")
    task = data.get("task")
    if not isinstance(task, str) or not _SLUG.match(task):
        errors.append("task: must be a slug")
    if data.get("type") != "prompt":
        errors.append("type: must be 'prompt'")
    source = data.get("source")
    if not isinstance(source, str) or not source:
        errors.append("source: must name the provenance")
    instructions = data.get("instructions")
    directive = instructions.get("core_directive") if isinstance(instructions, dict) else None
    if not isinstance(directive, str) or not directive.strip():
        errors.append("instructions.core_directive: the body is required")
    for legacy in ("content", "input"):
        if legacy in data:
            errors.append(f"{legacy}: legacy top-level body is refused")
    if "extends" in data and (not isinstance(data["extends"], str) or not data["extends"]):
        errors.append("extends: must be a non-empty string")
    if "compose" in data and data["compose"] not in COMPOSE_MODES:
        errors.append("compose: must be append, prepend or replace")
    for key in ("skills", "tools"):
        if key in data and not (
            isinstance(data[key], list) and all(isinstance(v, str) for v in data[key])
        ):
            errors.append(f"{key}: must be a list of strings")
    return errors


def save(blueprint: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(blueprint, indent=2) + "\n", encoding="utf-8")
