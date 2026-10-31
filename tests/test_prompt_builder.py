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

# The canonical validator lives in agent-utilities; skip cleanly if it (or an
# older installed copy without the canonical contract) is unavailable.
validate_canonical = pytest.importorskip(
    "agent_utilities.prompting.structured"
).__dict__.get("validate_canonical")

REPO = Path(__file__).resolve().parents[1]
PROMPT_BUILDER = (
    REPO / "universal_skills" / "skills" / "prompt-builder" / "scripts"
)

pytestmark = pytest.mark.skipif(
    validate_canonical is None,
    reason="installed agent-utilities predates the canonical prompt contract",
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
                "agent-utilities:base",
                "-o",
                str(out),
            ],
            capture_output=True,
            text=True,
        ).returncode
        assert rc == 0
        errs = validate_canonical(json.loads(out.read_text()))
        assert errs == []
