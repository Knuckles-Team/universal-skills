"""The package scaffold opts into the shared public documentation contract."""

from __future__ import annotations

import importlib.util
import re
import tomllib
from pathlib import Path


SCAFFOLD = (
    Path(__file__).parents[1]
    / "universal_skills"
    / "agent-tools"
    / "agent-package-builder"
    / "scripts"
    / "scaffold_package.py"
)
PIPELINES_REV = "35209bf6d85569a3c1fe3d5cd31771cacfdc3731"


def _load_scaffold():
    spec = importlib.util.spec_from_file_location("_public_surface_scaffold", SCAFFOLD)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _scaffold(
    tmp_path: Path, *, package_name: str, pkg_types: str = "api_client,mcp,agent"
) -> tuple[object, Path]:
    module = _load_scaffold()
    module.scaffold(package_name, output_dir=str(tmp_path), pkg_types=pkg_types)
    return module, tmp_path / package_name


def _headings(text: str) -> set[str]:
    return {
        re.sub(r"\s+", " ", match.group(2).strip(" #\t").lower())
        for match in re.finditer(
            r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$", text, re.MULTILINE
        )
    }


def test_generated_package_opts_into_public_surface(tmp_path: Path) -> None:
    module, root = _scaffold(tmp_path, package_name="example-provider")
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    config = pyproject["tool"]["pipelines_hooks"]["public_surface"]

    assert config == {
        "repository": "Knuckles-Team/example-provider",
        "distribution": "example-provider",
        "pages_url": "https://knuckles-team.github.io/example-provider/",
        "mcp_server": True,
    }
    assert pyproject["tool"]["pipelines_hooks"]["packages"] == ["example_provider"]

    pre_commit = (root / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert f"rev: {PIPELINES_REV}" in pre_commit
    assert "- id: public-surface" in pre_commit

    readme = (root / "README.md").read_text(encoding="utf-8")
    expected = module.render_public_badges("example-provider", mcp_server=True)
    assert expected in readme
    assert "![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')" in readme
    assert {
        "overview",
        "key capabilities",
        "quick start",
        "architecture",
        "documentation",
        "development",
        "license",
    } <= _headings(readme)
    assert len(readme) >= 1_500
    assert len(readme) <= 24_000
    assert len(readme.splitlines()) <= 200
    assert len(re.findall(r"^ {0,3}#(?!#)[ \t]+", readme, re.MULTILINE)) == 1

    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    assert {
        "what this repository owns",
        "architecture and module map",
        "commands",
        "quality gates",
        "development rules",
        "documentation",
        "branching & isolation",
    } <= _headings(agents)
    assert len(agents) >= 1_200
    assert len(agents) <= 24_000
    assert len(agents.splitlines()) <= 240
    assert len(re.findall(r"^ {0,3}#(?!#)[ \t]+", agents, re.MULTILINE)) == 1


def test_generated_mcp_badge_and_flag_follow_package_types(tmp_path: Path) -> None:
    module, root = _scaffold(
        tmp_path, package_name="api-provider", pkg_types="api_client,agent"
    )
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    config = pyproject["tool"]["pipelines_hooks"]["public_surface"]

    assert config["mcp_server"] is False
    readme = (root / "README.md").read_text(encoding="utf-8")
    assert "MCP Server" not in module.render_public_badges(
        "api-provider", mcp_server=False
    )
    assert "![MCP Server]" not in readme
