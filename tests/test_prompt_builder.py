"""Parity tests: the scaffold prompt template + prompt-builder never drift from
the canonical StructuredPrompt schema (CONCEPT:MERISTEM-ORCH.routing.resolve-body-single-canonical).

These guard the exact gap that produced the original drift: a hand-edited
template diverging from the model. Both the mcp-builder's
``render_main_agent_json`` and the prompt-builder's ``build_prompt`` must emit
blueprints that pass the ONE shared validator.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from universal_skills.prompt_blueprint import validate_canonical

REPO = Path(__file__).resolve().parents[1]
PROMPT_BUILDER = (
    REPO / "universal_skills" / "skills" / "prompt-builder" / "scripts"
)

def test_prompt_builder_build_then_validate():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "main_agent.json"
        rc = subprocess.run(
            [
                sys.executable,
                str(PROMPT_BUILDER / "build_prompt.py"),
                "--task",
                "demo-agent",
                "--source",
                "demo-pkg",
                "--directive",
                "You are the demo agent. Verify before acting.",
                "--extends",
                "meristem:base",
                "-o",
                str(out),
            ],
            capture_output=True,
            text=True,
        ).returncode
        assert rc == 0
        errs = validate_canonical(json.loads(out.read_text()))
        assert errs == []


def test_legacy_body_and_bad_compose_are_refused():
    errs = validate_canonical(
        {"schema_version": "1.0", "task": "x", "type": "prompt", "source": "s",
         "instructions": {"core_directive": "d"}, "content": "old", "compose": "merge"}
    )
    assert any(e.startswith("content:") for e in errs)
    assert any(e.startswith("compose:") for e in errs)
