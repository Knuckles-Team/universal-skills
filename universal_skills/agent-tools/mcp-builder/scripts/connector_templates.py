"""SDK-native connector content, ingestion, and live-contract scaffolds."""

from __future__ import annotations

import hashlib
import json
from textwrap import dedent


def _resource_name(domain: str) -> str:
    return (
        "".join(word.capitalize() for word in domain.replace("-", " ").split())
        + "Resource"
    )


def render_connector_manifest(source: str, domain: str, ontology_text: str) -> str:
    """Render YAML-compatible JSON with a real byte hash and no invented syncs."""
    resource = _resource_name(domain)
    manifest = {
        "connector": source,
        "ontology_source": domain,
        "schema_version": "1",
        "resources": [{"name": name} for name in (resource, "Document", "MediaAsset")],
        "identity": {"id_field": {resource: "id"}, "title_field": {resource: "name"}},
        "schema_mappings": {resource: {"fields": {"name": "xsd:string"}}},
        "sync": [],
        "provenance": {
            "generated_by": "mcp-builder/scripts/scaffold_package.py",
            "source_artifacts": [f"ontology/{domain}.ttl"],
            "integrity": {
                "algorithm": "sha256",
                "hash": hashlib.sha256(ontology_text.encode("utf-8")).hexdigest(),
            },
        },
        "review_todos": [
            "Replace the starter resource mapping with the reviewed source model.",
            "Declare real source presets and matching sync entries before certification.",
            "Integrity is an ontology byte hash, not canonical RDF or release certification.",
        ],
    }
    return json.dumps(manifest, indent=2) + "\n"


def render_empty_fingerprints(source: str) -> str:
    """No extraction presets means there are no extraction tool pins yet."""
    return (
        json.dumps(
            {
                "connector": source,
                "algorithm": "agent-connector-sdk:mcp-tool-contract-compat:v2",
                "tools": {},
            },
            indent=2,
        )
        + "\n"
    )


def render_kg_ingest(display_name: str, pkg_dir: str, source: str, domain: str) -> str:
    """Map source data through SDK models; never reproduce engine DTOs."""
    del pkg_dir
    template = '''\
"""Typed source observations for __DISPLAY__, submitted through the SDK.

The configured ingest service owns durable checkpoints and engine transport.
These helpers perform no work at import time; missing configuration and rejected
submissions propagate to the caller. Invoke only for authorized source reads.
"""

from __future__ import annotations

from typing import Any

from agent_connector_sdk.ingest import (
    ChangeSet,
    Document,
    Entity,
    IngestBinding,
    KnowledgeIngest,
    MediaAsset,
    current_ingest,
)

_BINDING = IngestBinding(connector=__SOURCE__, stream=__DOMAIN__)


async def _submit(changes: ChangeSet, ingest: KnowledgeIngest | None) -> dict[str, int]:
    service = ingest if ingest is not None else current_ingest()
    receipt = await service.submit(_BINDING, changes)
    return {"nodes": receipt.affected_count, "edges": receipt.relationship_count}


async def ingest_records(
    records: list[dict[str, Any]], *, ingest: KnowledgeIngest | None = None
) -> dict[str, int]:
    """Submit records as the starter manifest resource; adapt the mapping first."""
    entities = []
    for record in records:
        record_id = record.get("id")
        if record_id is None or not str(record_id).strip():
            raise ValueError("each source record needs a stable id")
        entities.append(
            Entity(
                id=str(record_id),
                node_type=__RESOURCE__,
                properties={
                    "name": record.get("name") or record.get("title") or str(record_id)
                },
            )
        )
    if not entities:
        raise ValueError("ingest_records needs at least one record")
    return await _submit(ChangeSet(entities=tuple(entities)), ingest)


async def ingest_documents(
    docs: list[dict[str, Any]], *, ingest: KnowledgeIngest | None = None
) -> dict[str, int]:
    """Submit text through SDK Document models, preserving the source identity."""
    if not docs:
        raise ValueError("ingest_documents needs at least one document")
    documents = tuple(
        Document(
            id=str(doc["id"]),
            text=doc["text"],
            title=doc.get("title"),
            source_uri=doc.get("source_uri"),
        )
        for doc in docs
    )
    return await _submit(ChangeSet(documents=documents), ingest)


async def ingest_blob(
    data: bytes,
    *,
    mime_type: str,
    name: str = "",
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Submit media through SDK MediaAsset; storage belongs to the engine."""
    if not data or not mime_type.strip():
        raise ValueError("media requires non-empty bytes and a MIME type")
    return await _submit(
        ChangeSet(
            media=(
                MediaAsset(
                    data=data,
                    mime_type=mime_type,
                    name=name,
                ),
            )
        ),
        ingest,
    )
'''
    return (
        template.replace("__DISPLAY__", display_name)
        .replace("__SOURCE__", repr(source))
        .replace("__DOMAIN__", repr(domain))
        .replace("__RESOURCE__", repr(_resource_name(domain)))
    )


def render_kg_ingest_test(pkg_dir: str) -> str:
    """Use a fake submission boundary with the real SDK typed change sets."""
    return dedent('''\
"""Contract checks for source mapping; no engine or service connection."""

import asyncio
from types import SimpleNamespace

import pytest

from __PACKAGE__ import kg_ingest


class FakeIngest:
    def __init__(self):
        self.calls = []

    async def submit(self, binding, changes):
        self.calls.append((binding, changes))
        return SimpleNamespace(affected_count=1, relationship_count=0)


def test_ingest_maps_record_and_uses_submit():
    fake = FakeIngest()
    assert asyncio.run(
        kg_ingest.ingest_records([{"id": 0, "name": "first"}], ingest=fake)
    ) == {"nodes": 1, "edges": 0}
    binding, changes = fake.calls[0]
    assert binding.connector
    assert changes.entities[0].id == "0"
    assert changes.entities[0].properties == {"name": "first"}
    assert changes.withdrawals == ()


def test_missing_identity_fails_before_submit():
    fake = FakeIngest()
    with pytest.raises(ValueError, match="stable id"):
        asyncio.run(kg_ingest.ingest_records([{"name": "missing"}], ingest=fake))
    assert not fake.calls


def test_documents_and_media_use_typed_changes():
    fake = FakeIngest()
    asyncio.run(
        kg_ingest.ingest_documents([{"id": "doc", "text": "content"}], ingest=fake)
    )
    asyncio.run(kg_ingest.ingest_blob(b"content", mime_type="text/plain", ingest=fake))
    assert fake.calls[0][1].documents[0].text == "content"
    assert fake.calls[1][1].media[0].data == b"content"


def test_submit_failure_propagates():
    class RejectedIngest:
        async def submit(self, binding, changes):
            raise RuntimeError("rejected source")

    with pytest.raises(RuntimeError, match="rejected source"):
        asyncio.run(kg_ingest.ingest_records([{"id": "one"}], ingest=RejectedIngest()))
''').replace("__PACKAGE__", pkg_dir)


def render_schema_generator(pkg_dir: str, source: str) -> str:
    """Capture live tools/list; pin only real declared extraction presets."""
    return (
        dedent('''\
#!/usr/bin/env python3
"""Generate or check live MCP contracts without calling provider tools.

Run from the project environment: python scripts/generate_tool_schemas.py [--check].
All tools retain both schemas in schemas/mcp_tools.json. Only tools in real
extraction presets receive connector pins; an empty starter preset is valid.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from agent_connector_sdk.manifest.live_contract import validate_live_tool_contract
    from agent_connector_sdk.manifest.loader import (
        load_tool_presets,
        require_valid_connector_package,
    )
    from agent_connector_sdk.manifest.tool_schema import (
        COMPATIBILITY_FINGERPRINT_ALGORITHM,
        canonical_input_schema,
        canonical_output_schema,
    )
    from fastmcp import Client

    from __PACKAGE__.mcp_server import build_server
except ImportError as exc:
    raise SystemExit(
        "Install this project's declared dependencies before generating schemas"
    ) from exc

PACKAGE = ROOT / "__PACKAGE__"


def _write_or_check(path: Path, value: dict, check: bool) -> None:
    text = json.dumps(value, indent=2, sort_keys=True) + "\\n"
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"Stale generated contract: {path.relative_to(ROOT)}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


async def generate(check: bool) -> None:
    async with Client(build_server(command_args=["--transport", "stdio"])) as client:
        tools = await client.list_tools()
    contracts = {}
    for tool in tools:
        contract = validate_live_tool_contract(tools, tool_name=tool.name)
        contracts[tool.name] = {
            "inputSchema": canonical_input_schema(tool),
            "outputSchema": canonical_output_schema(tool),
            "compatibility_sha256": contract.compatibility_sha256,
        }
    presets = load_tool_presets(PACKAGE / "connectors/mcp_source_presets.json")
    pinned = {
        preset.tool: contracts[preset.tool]["compatibility_sha256"]
        for preset in presets.values()
    }
    _write_or_check(
        ROOT / "schemas/mcp_tools.json",
        {
            "algorithm": COMPATIBILITY_FINGERPRINT_ALGORITHM,
            "tools": contracts,
        },
        check,
    )
    _write_or_check(
        PACKAGE / "connectors/tool_schema_fingerprints.json",
        {
            "connector": "__SOURCE__",
            "algorithm": COMPATIBILITY_FINGERPRINT_ALGORITHM,
            "tools": pinned,
        },
        check,
    )
    require_valid_connector_package(PACKAGE)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    asyncio.run(generate(parser.parse_args().check))
''')
        .replace("__PACKAGE__", pkg_dir)
        .replace("__SOURCE__", source)
    )
