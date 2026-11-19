"""US-CONTENT-R001.4: the connector pack imports into the engine and its schema attaches.

The deploy step of the graph door builds this package's connector pack with
the SDK, imports it through ``ConnectorPack.Import``, waits for the pack to
project and attaches its schema with ``GraphSchema`` ``attach_pack``. Its
readiness check then requires the attached source to carry both an ontology
and SHACL shapes. This test runs that path against a loopback engine started
in the explicit no-auth mode (tenant ``local``, principal ``anonymous``).

The engine server binary ships in the platform wheels of ``medulla``; without
it the test skips with the reason, because the in-process engine serves no
``ConnectorPack`` operation.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib.metadata
import os
import signal
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

pytestmark = pytest.mark.spec("US-CONTENT-R001.4")

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "universal_skills"
CONNECTOR = "universal-skills"
#: The identity the engine binds in its no-auth mode, and that principal's
#: persistence id (the engine binds a connector's importer by this id).
TENANT = "local"
PRINCIPAL = "principal:sha256:" + hashlib.sha256(b"anonymous").hexdigest()
PROJECTION_WAIT_SECS = 120.0


def _engine_binary() -> str | None:
    try:
        from medulla.server_binary import resolve_server_binary

        return resolve_server_binary()
    except Exception:  # ImportError or ServerBinaryNotFoundError
        return None


async def _connect(process: subprocess.Popen[bytes], socket_path: Path) -> Any:
    from medulla.client import MedullaClient

    deadline = time.monotonic() + 30.0
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise AssertionError("the loopback engine exited while starting")
        if socket_path.exists():
            try:
                return await asyncio.wait_for(
                    MedullaClient.connect(
                        socket_path=str(socket_path), auth_mode="none"
                    ),
                    timeout=5.0,
                )
            except (OSError, ConnectionError):
                pass
        await asyncio.sleep(0.2)
    raise AssertionError("the loopback engine did not serve its socket in time")


@pytest.fixture
async def engine(tmp_path: Path) -> Any:
    binary = _engine_binary()
    if binary is None:
        pytest.skip(
            "the medulla server binary is not installed; the served "
            "ConnectorPack.Import path needs a loopback engine"
        )
    socket_path = tmp_path / "medulla.sock"
    persist_dir = tmp_path / "persist"
    persist_dir.mkdir()
    process = subprocess.Popen(
        [
            binary,
            "--auth-mode",
            "none",
            "--socket-path",
            str(socket_path),
            "--persist-dir",
            str(persist_dir),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        # The deploy binds each connector to the principal allowed to import it.
        env={**os.environ, "MEDULLA_CONNECTOR_PACK_IMPORTERS": f"{CONNECTOR}={PRINCIPAL}"},
    )
    client = None
    try:
        client = await _connect(process, socket_path)
        yield client
    finally:
        if client is not None:
            await client.close()
        process.send_signal(signal.SIGTERM)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


async def _pack() -> Any:
    from scion_sdk.artifacts.pack import build_connector_content_pack
    from scion_sdk.mcp.content import ConnectorContent

    content = ConnectorContent.for_package(
        "universal_skills", PKG, importlib.metadata.version("universal-skills")
    )
    assert content.connector == CONNECTOR
    return await build_connector_content_pack(content)


async def _import(client: Any, pack: Any) -> Any:
    from medulla.generated._shared import (
        AgentLibraryMutationContext,
        McpCatalogSnapshotBinding,
    )
    from scion_sdk.sinks.medulla import MedullaSink

    zero = "0" * 64

    async def authority(_connector: str) -> Any:
        catalog = McpCatalogSnapshotBinding(
            authorization_scope_digest=zero,
            catalog_generation=1,
            child_connection_generation=1,
            configuration_revision=1,
            snapshot_digest=zero,
        )
        context = AgentLibraryMutationContext(
            actor_scope="universal-skills:content-import",
            attempt_nonce=zero,
            caller_principal=PRINCIPAL,
            created_at_ms=0,
            idempotency_key="universal-skills:content-import",
            policy_decision_id="universal-skills:policy-decision",
            policy_digest=zero,
            policy_revision="universal-skills:v1",
            principal=PRINCIPAL,
            purpose_id="universal-skills:content-import",
            request_id=1,
            tenant_id=TENANT,
        )
        return catalog, context

    return await MedullaSink(client, pack_import_authority=authority).import_pack(
        pack
    )


async def _await_projection(client: Any) -> str:
    from medulla.generated.connector_pack import ConnectorPackStatusRequest
    from medulla.generated.storage import send_connector_pack_status

    deadline = time.monotonic() + PROJECTION_WAIT_SECS
    while True:
        status = await send_connector_pack_status(
            client, ConnectorPackStatusRequest(connector=CONNECTOR, tenant_id=TENANT)
        )
        state = str(getattr(status.projection, "projection", "none"))
        if state in {"applied", "failed"} or time.monotonic() >= deadline:
            return state
        await asyncio.sleep(0.5)


def test_every_class_rolls_up_to_core() -> None:
    """Every declared class reaches a core class; no core class is redeclared."""
    from scion_sdk.testing.ontology_rollup import (
        CORE_NAMESPACE,
        orphan_classes,
        parse_triples,
    )

    files = sorted((PKG / "ontology").glob("*.ttl"))
    assert files
    assert sorted((PKG / "ontology" / "shapes").glob("*.ttl"))
    owl_class = "http://www.w3.org/2002/07/owl#Class"
    for path in files:
        assert not orphan_classes(path), path.name
        declared = {
            s for s, p, o in parse_triples(path.read_text(encoding="utf-8"))
            if o == owl_class
        }
        assert declared
        assert not {c for c in declared if c.startswith(CORE_NAMESPACE)}


# Building the 268-skill pack and projecting it takes longer than the default
# per-test budget on a loaded runner.
@pytest.mark.timeout(300)
async def test_pack_imports_and_attaches_with_ontology_and_shapes(engine: Any) -> None:
    """The receipt holds no ONTOLOGY_ warning and the attached source has shapes."""
    from medulla.generated.connector_pack import PackImportResultImported
    from medulla.generated.reasoning import (
        send_graph_schema,
        send_graph_schema_list,
    )

    pack = await _pack()
    kinds = Counter(entry.kind.value for entry in pack.archive.entries)
    assert kinds["ontology"] >= 1
    assert kinds["shapes"] >= 1
    assert kinds["skill"] >= 1

    result = await _import(engine, pack)
    assert isinstance(result, PackImportResultImported), result
    receipt = result.receipt
    assert receipt.connector == CONNECTOR
    assert receipt.tenant_id == TENANT
    codes = [warning.code.value for warning in receipt.warnings]
    assert not [c for c in codes if c.startswith(("ONTOLOGY", "ATTACH"))], codes

    assert await _await_projection(engine) == "applied"
    await send_graph_schema(
        engine, {"op": {"op": "attach_pack", "connector": CONNECTOR}}
    )

    view = await send_graph_schema_list(engine, {})
    source = next(
        s for s in view.dynamic_sources if s.source_id == f"pack:{CONNECTOR}"
    )
    assert source.origin.origin == "pack"
    assert source.origin.connector == CONNECTOR
    assert source.ontology_sha256
    assert source.shapes_sha256
