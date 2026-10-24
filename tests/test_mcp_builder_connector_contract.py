"""SDK contract tests for generated connector content and typed ingestion."""

from __future__ import annotations

import ast
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

HELPER = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts/connector_templates.py"
)


def _module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def templates():
    return _module(HELPER, "connector_templates_test")






def _declare_fleet_name(root: Path, package: str, fleet: str) -> None:
    (root / "pyproject.toml").write_text(
        '[project]\nname = "example"\nversion = "0.0.0"\n\n'
        '[project.entry-points."agent_connector_sdk.connector"]\n'
        f'{fleet} = "{package}"\n',
        encoding="utf-8",
    )


def _package(tmp_path: Path, templates) -> Path:
    _declare_fleet_name(tmp_path, "example", "example-mcp")
    package = tmp_path / "example"
    (package / "connectors").mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "connector_manifest.yml").write_text(
        templates.render_connector_manifest("example-mcp", "example", ""),
        encoding="utf-8",
    )
    (package / "connectors/mcp_source_presets.json").write_text(
        "{}\n", encoding="utf-8"
    )
    (package / "connectors/tool_schema_fingerprints.json").write_text(
        templates.render_empty_fingerprints("example-mcp"),
        encoding="utf-8",
    )
    return package






def test_schema_generator_captures_both_live_schemas(tmp_path, templates, monkeypatch):
    pytest.importorskip("agent_connector_sdk.mcp.server")
    package = _package(tmp_path, templates)
    (package / "mcp_server.py").write_text(
        "from fastmcp import FastMCP\n\n"
        "def build_server(*, command_args):\n"
        "    mcp = FastMCP('example-mcp')\n"
        "    @mcp.tool()\n"
        "    def echo(value: str) -> str:\n"
        "        return value\n"
        "    return mcp\n",
        encoding="utf-8",
    )
    script = tmp_path / "scripts/generate_tool_schemas.py"
    script.parent.mkdir()
    script.write_text(templates.render_schema_generator("example", "example-mcp"))
    monkeypatch.syspath_prepend(str(tmp_path))
    module = _module(script, "generated_schema_script")
    asyncio.run(module.generate(False))
    asyncio.run(module.generate(True))
    schemas = tmp_path / "schemas/mcp_tools.json"
    assert len(schemas.read_text().splitlines()) == 1
    contract = json.loads(schemas.read_text())["tools"]["echo"]
    assert contract["inputSchema"]["properties"]["value"]["type"] == "string"
    assert contract["outputSchema"] is not None
    assert len(contract["compatibility_sha256"]) == 64
    pins = json.loads(
        (package / "connectors/tool_schema_fingerprints.json").read_text()
    )
    assert pins["algorithm"] == "agent-connector-sdk:mcp-tool-contract-compat:v2"
    assert pins["tools"] == {}
    schemas.write_text("{}\n")
    with pytest.raises(SystemExit, match="Stale generated contract"):
        asyncio.run(module.generate(True))
