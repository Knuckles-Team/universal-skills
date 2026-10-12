"""Generated Pages inputs and dashboard config follow the shared contract."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml


SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)
PIPELINES_REF = "main"


@pytest.fixture
def generated(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "scaffold_package.py"),
            "pages-example",
            "--output-dir",
            str(tmp_path),
        ],
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    root = tmp_path / "pages-example"
    workflow = yaml.safe_load((root / ".github/workflows/pages.yml").read_text())
    return root, workflow


def test_generated_pages_opts_into_canonical_delivery(generated):
    root, workflow = generated
    job = workflow["jobs"]["publish-pages"]
    assert job["uses"].endswith("pages_pipeline.yml@" + PIPELINES_REF)
    assert job["with"] == {
        "content_source": "docs",
        "shared_theme_enabled": True,
        "agent_readiness_enabled": True,
        "readiness_input": "docs/agent-readiness.json",
        "readiness_schema": "docs/agent-readiness.schema.json",
        "spec_dashboard_enabled": True,
        "spec_dashboard_config": ".config/spec-dashboard.json",
    }
    trigger = workflow.get("on", workflow.get(True))
    assert trigger["push"] == {"branches": ["main"]}
    assert "workflow_dispatch" in trigger
    for key in ("readiness_input", "readiness_schema", "spec_dashboard_config"):
        assert (root / job["with"][key]).is_file()
    assert json.loads((root / job["with"]["spec_dashboard_config"]).read_text()) == {
        "version": 1,
        "sources": [{"glob": "specs/*/status.json", "kind": "spec"}],
    }
    documentation = (root / "docs/spec-delivery.md").read_text()
    assert (
        "https://knuckles-team.github.io/pages-example/spec-delivery/" in documentation
    )
    assert "**SPECIFIED**" in documentation
    assert "spec-delivery" in (root / "mkdocs.yml").read_text()


def test_generated_delivery_passes_pinned_pipeline_contract(generated):
    source = os.environ.get("PIPELINES_CONTRACT_ROOT")
    if not source:
        pytest.skip(
            "set PIPELINES_CONTRACT_ROOT to the reviewed pinned pipeline source snapshot"
        )
    pipeline = Path(source)
    root, workflow = generated
    shared = yaml.safe_load(
        (pipeline / ".github/workflows/pages_pipeline.yml").read_text()
    )
    declared = shared.get("on", shared.get(True))["workflow_call"]["inputs"]
    for name, value in workflow["jobs"]["publish-pages"]["with"].items():
        assert name in declared
        expected = {"boolean": bool, "string": str}[declared[name]["type"]]
        assert type(value) is expected
    # Call the pipeline-owned config parser and source reader, never a local clone
    # of their validation rules. These operations do not fetch GitHub or render.
    code = (
        "import sys; sys.path.insert(0, sys.argv[1]); "
        "from spec_dashboard import parse_options, read_records; "
        "args, root, config = parse_options(['--root', sys.argv[2], "
        "'--config', '.config/spec-dashboard.json', '--repository', "
        "'Knuckles-Team/pages-example']); "
        "assert config['version'] == 1; rows = read_records(root, config); assert rows; assert all(row['delivery_state'] == 'SPECIFIED' for row in rows)"
    )
    checked = subprocess.run(
        [sys.executable, "-c", code, str(pipeline / "scripts"), str(root)],
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert checked.returncode == 0, checked.stdout + checked.stderr
    readiness = subprocess.run(
        [
            sys.executable,
            str(pipeline / "scripts/pages_readiness.py"),
            "validate-content-source",
            "--root",
            str(root),
            "--content-source",
            "docs",
        ],
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert readiness.returncode == 0, readiness.stdout + readiness.stderr
