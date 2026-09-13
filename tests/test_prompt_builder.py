"""prompt-builder emits blueprints that pass the canonical StructuredPrompt
validator (CONCEPT:AU-ORCH.routing.resolve-body-single-canonical).

Until RF-ADR-009 (lane BUILDER-RETARGET), this file also guarded parity
between agent-package-builder's generated prompt template and this schema.
That coupling is gone by design: the retargeted agent-package-builder scaffold
depends on agent-connector-sdk only and generates the SDK's own MCP prompt
shape (``instructions.core_directive``, validated by
``agent_connector_sdk.mcp.content``), not agent-utilities' canonical
StructuredPrompt — see
``universal_skills/agent-tools/agent-package-builder/PARITY_MANIFEST.md``.
prompt-builder itself is unaffected and still targets agent-utilities
providers, so its own contract is still checked here.
"""

from __future__ import annotations

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
    REPO / "universal_skills" / "agent-tools" / "prompt-builder" / "scripts"
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
