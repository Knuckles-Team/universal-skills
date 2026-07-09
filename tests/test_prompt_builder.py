"""Parity tests: the scaffold prompt template + prompt-builder never drift from
the canonical StructuredPrompt schema (CONCEPT:AU-ORCH.routing.resolve-body-single-canonical).

These guard the exact gap that produced the original drift: a hand-edited
template diverging from the model. Both the agent-package-builder's
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
SCAFFOLD = (
    REPO
    / "universal_skills"
    / "agent-tools"
    / "agent-package-builder"
    / "scripts"
    / "scaffold_package.py"
)
PROMPT_BUILDER = (
    REPO / "universal_skills" / "agent-tools" / "prompt-builder" / "scripts"
)

pytestmark = pytest.mark.skipif(
    validate_canonical is None,
    reason="installed agent-utilities predates the canonical prompt contract",
)


def _load_scaffold_module():
    spec = importlib.util.spec_from_file_location("_scaffold_pkg", SCAFFOLD)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_scaffold_main_agent_template_is_canonical():
    mod = _load_scaffold_module()
    rendered = mod.render_main_agent_json("Widget", "Widget Api Agent.", "widget-api")
    data = json.loads(rendered)
    errs = validate_canonical(data, strict=True)
    assert errs == [], f"scaffold main_agent template drifted from canonical: {errs}"
    assert data["source"] == "widget-api"
    assert data["instructions"]["core_directive"].strip()


def test_scaffold_starter_skill_has_frontmatter():
    mod = _load_scaffold_module()
    md = mod.render_starter_skill("Widget", "widget-starter", "Widget Api Agent.")
    assert md.startswith("---\nname: widget-starter\n")
    assert "description:" in md
    # Atomic: no multi-step DAG markers.
    assert "depends_on:" not in md


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
        errs = validate_canonical(json.loads(out.read_text()), strict=True)
        assert errs == []
