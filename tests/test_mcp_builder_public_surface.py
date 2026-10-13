"""The scaffold consumes the shared reader-facing documentation contract."""

import importlib.util
import tomllib
from pathlib import Path

import yaml


SCAFFOLD = (
    Path(__file__).parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts/scaffold_package.py"
)
PIPELINES_REF = "main"


def _load_scaffold():
    spec = importlib.util.spec_from_file_location("_public_surface_scaffold", SCAFFOLD)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_package_consumes_public_surface_and_declares_package(tmp_path):
    module = _load_scaffold()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"
    project = tomllib.loads((root / "pyproject.toml").read_text())
    assert project["tool"]["pipelines_hooks"]["packages"] == ["example_provider"]
    hooks = yaml.safe_load((root / ".pre-commit-config.yaml").read_text())["repos"]
    shared = next(
        repo
        for repo in hooks
        if repo["repo"] == "https://github.com/Knuckles-Team/pipelines"
    )
    assert shared["rev"] == PIPELINES_REF
    assert {"id": "public-surface"} in shared["hooks"]
    readme = (root / "README.md").read_text()
    assert "pip install" in readme or "uv sync" in readme
    assert (root / "AGENTS.md").is_file()
    # Wording, length, badges and heading layout are review guidance, not gates.


def test_supported_scaffold_advertises_its_mcp_surface(tmp_path):
    module = _load_scaffold()
    module.scaffold(
        "api-provider", output_dir=str(tmp_path), pkg_types="api_client,mcp"
    )
    readme = (tmp_path / "api-provider/README.md").read_text()
    assert "![MCP Server]" in readme
    assert "MCP Server" not in module.render_public_badges(
        "api-provider", mcp_server=False
    )
