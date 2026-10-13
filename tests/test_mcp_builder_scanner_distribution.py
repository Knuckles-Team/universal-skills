"""Distribution and rerun contracts for shared pipeline consumption."""

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SCAFFOLD = (
    Path(__file__).parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts/scaffold_package.py"
)
PIPELINES_REF = "main"


def _load_scaffold():
    spec = importlib.util.spec_from_file_location(
        "_scanner_distribution_scaffold", SCAFFOLD
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _workflow(text):
    # BaseLoader preserves GitHub's `on` key instead of YAML 1.1 true.
    return yaml.load(text, Loader=yaml.BaseLoader)


def test_regular_ci_runs_project_hooks_and_tests_without_release_readiness():
    workflow = _workflow(_load_scaffold().SCANNER_CI_YML)
    assert {"pull_request", "push"} <= workflow["on"].keys()
    assert workflow["permissions"] == {"contents": "read"}
    commands = "\n".join(
        step.get("run", "")
        for job in workflow["jobs"].values()
        for step in job["steps"]
    )
    assert '"$CONNECTOR_PRE_COMMIT" run --all-files' in commands
    assert "--hook-stage pre-push" in commands
    assert "--hook-stage manual" not in commands
    assert "dependency-readiness" not in commands
    assert "continue-on-error" not in _load_scaffold().SCANNER_CI_YML
    steps = workflow["jobs"]["checks"]["steps"]
    assert "command -v pre-commit" in steps[1]["run"]
    assert steps[4]["run"] == "python scripts/bootstrap_environment.py --github"
    assert "validate-config" in steps[5]["run"]
    assert "python -m pre_commit" not in commands
    assert workflow["jobs"]["checks"]["env"]["MCP_FLEET_REGISTRATION"] == "false"


@pytest.mark.parametrize("floor", ["3.12", "3.13"])
def test_ci_provisions_declared_floor_before_frozen_bootstrap(tmp_path, floor):
    steps = _workflow(_load_scaffold().SCANNER_CI_YML)["jobs"]["checks"]["steps"]
    resolver, setup, bootstrap = steps[2:5]
    assert resolver["id"] == "python-baseline"
    assert setup["uses"] == (
        "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065"
    )
    assert setup["with"]["python-version"] == (
        "${{ steps.python-baseline.outputs.version }}"
    )
    assert bootstrap["run"] == "python scripts/bootstrap_environment.py --github"
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copyfile(
        SCAFFOLD.parent / "bootstrap_sources.py", scripts / "bootstrap_sources.py"
    )
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nrequires-python = ">={floor}, <3.15"\n'
        "[project.optional-dependencies]\ntest = []\n"
    )
    (tmp_path / "uv.lock").write_text("package = []\n")
    output = tmp_path / "github-output"
    env = dict(os.environ, GITHUB_OUTPUT=str(output))
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env["PATH"]
    subprocess.run(
        ["bash", "-e", "-c", resolver["run"]], cwd=tmp_path, env=env, check=True
    )
    assert output.read_text() == f"version={floor}\n"


def test_release_reuses_shared_pipeline_only_for_version_tags():
    workflow = _workflow(_load_scaffold().PIPELINE_YML)
    assert workflow["on"] == {"push": {"tags": ["v*"]}}
    job = workflow["jobs"]["publish-pypi"]
    assert job["uses"] == (
        "Knuckles-Team/pipelines/.github/workflows/python_pipeline.yml@" + PIPELINES_REF
    )
    assert job["if"] == "startsWith(github.ref, 'refs/tags/v')"
    assert job["secrets"] == {"PYPI_API_TOKEN": "${{ secrets.PYPI_API_TOKEN }}"}


def test_pages_uses_shared_workflow_and_actual_content_root():
    workflow = _workflow(_load_scaffold().PAGES_YML)
    job = workflow["jobs"]["publish-pages"]
    assert job["uses"].endswith("pages_pipeline.yml@" + PIPELINES_REF)
    assert job["with"]["content_source"] == "docs"


def test_source_distribution_carries_hooks_without_copied_scanners():
    manifest = _load_scaffold().MANIFEST_IN
    assert "include .pre-commit-config.yaml" in manifest
    assert "graft .github/workflows" in manifest
    assert "graft scripts" in manifest
    assert "check_scanners.py" not in manifest
    assert "run_kiss.sh" not in manifest


def test_scaffold_rerun_preserves_project_owned_quality_files(tmp_path):
    module = _load_scaffold()
    module.scaffold("scanner-provider", output_dir=str(tmp_path))
    root = tmp_path / "scanner-provider"
    paths = [root / ".pre-commit-config.yaml", root / ".github/workflows/scanners.yml"]
    for name in ("bootstrap_environment.py", "bootstrap_sources.py"):
        assert (root / "scripts" / name).read_bytes() == (
            SCAFFOLD.parent / name
        ).read_bytes()
    assert "/.ci/" in (root / ".gitignore").read_text().splitlines()
    for path in paths:
        path.write_text(path.read_text() + "\n# operator-owned\n")
    expected = [path.read_bytes() for path in paths]
    module.scaffold("scanner-provider", output_dir=str(tmp_path))
    assert [path.read_bytes() for path in paths] == expected
