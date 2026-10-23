"""US-MCP-BUILDER-SCAFFOLD-R001: the scaffold names a connector by its fleet name."""

from __future__ import annotations

import importlib.util
import json
import tomllib
from pathlib import Path

import pytest

pytestmark = pytest.mark.spec("US-MCP-BUILDER-SCAFFOLD-R001")

SCAFFOLD = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts/scaffold_package.py"
)


def test_scaffold_names_the_connector_by_its_fleet_name(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location("_fleet_name_scaffold", SCAFFOLD)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.scaffold(
        "example-provider", output_dir=str(tmp_path), pkg_types="api_client,mcp"
    )
    root = tmp_path / "example-provider"
    package = root / "example_provider"
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    group = pyproject["project"]["entry-points"]["agent_connector_sdk.connector"]
    assert group == {"example-provider-mcp": "example_provider"}
    manifest = json.loads(
        (package / "connector_manifest.yml").read_text(encoding="utf-8")
    )
    assert manifest["connector"] == "example-provider-mcp"
    fingerprints = json.loads(
        (package / "connectors" / "tool_schema_fingerprints.json").read_text(
            encoding="utf-8"
        )
    )
    assert fingerprints["connector"] == "example-provider-mcp"
    server = (package / "mcp_server.py").read_text(encoding="utf-8")
    ingest = (package / "kg_ingest.py").read_text(encoding="utf-8")
    assert "ConnectorContent.for_package(" in server
    assert "IngestBinding.for_package(" in ingest
    assert 'connector="example-provider"' not in server + ingest
