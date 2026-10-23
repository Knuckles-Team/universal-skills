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


def test_templates_have_valid_python_and_no_legacy_imports(templates):
    outputs = (
        templates.render_kg_ingest("Example", "example", "example-mcp", "example"),
        templates.render_kg_ingest_test("example"),
        templates.render_schema_generator("example", "example-mcp"),
    )
    for source in outputs:
        tree = ast.parse(source)
        assert not any(
            isinstance(node, ast.ImportFrom)
            and (node.module or "").startswith("agent_utilities")
            for node in ast.walk(tree)
        )


def test_manifest_hashes_actual_ontology_and_declares_no_fake_sources(templates):
    ontology = "@prefix : <https://example.test/> .\n"
    data = json.loads(
        templates.render_connector_manifest("example-mcp", "example", ontology)
    )
    assert data["provenance"]["integrity"] == {
        "algorithm": "sha256",
        "hash": hashlib.sha256(ontology.encode()).hexdigest(),
    }
    assert data["sync"] == []
    assert {resource["name"] for resource in data["resources"]} == {
        "ExampleResource",
        "Document",
        "MediaAsset",
    }


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


def test_manifest_passes_current_sdk_package_validation(tmp_path, templates):
    loader = pytest.importorskip("agent_connector_sdk.manifest.loader")
    manifest = loader.require_valid_connector_package(_package(tmp_path, templates))
    assert manifest.connector == "example-mcp"


def test_ingestion_uses_real_sdk_models_with_fake_submission(
    tmp_path, templates, monkeypatch
):
    ingest = pytest.importorskip("agent_connector_sdk.ingest")
    package = tmp_path / "generated_kg_ingest"
    package.mkdir()
    (package / "__init__.py").write_text(
        templates.render_kg_ingest("Example", "example", "example-mcp", "example")
    )
    _declare_fleet_name(tmp_path, "generated_kg_ingest", "example-mcp")
    monkeypatch.syspath_prepend(str(tmp_path))
    module = importlib.import_module("generated_kg_ingest")
    calls = []

    class FakeIngest:
        async def submit(self, binding, changes):
            from types import SimpleNamespace

            calls.append((binding, changes))
            return SimpleNamespace(affected_count=1, relationship_count=0)

    result = asyncio.run(
        module.ingest_records([{"id": 0, "name": "first"}], ingest=FakeIngest())
    )
    assert result == {"nodes": 1, "edges": 0}
    binding, changes = calls[0]
    assert isinstance(binding, ingest.IngestBinding)
    assert isinstance(changes, ingest.ChangeSet)
    assert changes.entities == (
        ingest.Entity("0", "ExampleResource", {"name": "first"}),
    )
    with pytest.raises(ValueError, match="stable id"):
        asyncio.run(module.ingest_records([{"name": "missing"}], ingest=FakeIngest()))
    assert len(calls) == 1


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
