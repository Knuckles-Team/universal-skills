"""Epistemic-graph typed-node ingestion -- Wire-First coverage for wger-agent.

Exercises the real ``ingest_entities`` + wger record mappers against a fake
``agent_connector_sdk.ingest`` transport (no engine required). The real SDK request
builder (``agent_connector_sdk.ingest.request.build_request``) still runs, so a
malformed change set is still caught by the SDK's own contract, not re-derived here;
only the final network commit is faked.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from agent_connector_sdk.ingest import IngestError, KnowledgeIngest
from epistemic_graph.generated.source_ingestion import SourceIngestionRequest

from wger_agent.kg_ingest import (
    _records,
    ingest_entities,
    ingest_exercises,
    ingest_nutrition_plans,
    ingest_routines,
    ingest_workout_sessions,
)


class _FakeTransport:
    """Records every submitted request; no epistemic-graph engine required."""

    def __init__(self) -> None:
        self.requests: list[SourceIngestionRequest] = []

    async def source_status(self, _connector: str, _stream: str) -> Any:
        return SimpleNamespace(accepted_checkpoint=None)

    async def submit(self, request: SourceIngestionRequest) -> Any:
        self.requests.append(request)
        return SimpleNamespace(
            affected_count=len(request.records),
            relationship_count=len(request.relationships),
        )

    async def store_blob(self, _data: bytes) -> str:
        raise AssertionError("wger-agent wellness ingestion carries no media")


@pytest.fixture
def ingest() -> tuple[KnowledgeIngest, _FakeTransport]:
    transport = _FakeTransport()
    return KnowledgeIngest(transport, loop=None), transport


@pytest.mark.asyncio
async def test_ingest_entities_writes_nodes_and_edges(ingest):
    service, transport = ingest
    res = await ingest_entities(
        [
            {"id": "a", "node_type": "WorkoutSession"},
            {"id": "b", "node_type": "WorkoutRoutine"},
        ],
        [{"source": "a", "target": "b", "relationship": "sessionOfRoutine"}],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert len(transport.requests) == 1
    request = transport.requests[0]
    record_ids = {record.record_id for record in request.records}
    assert record_ids == {"a", "b"}
    assert request.relationships[0].relation_reference.endswith(
        "resources/WorkoutSession/relations/sessionOfRoutine"
    )


@pytest.mark.asyncio
async def test_ingest_exercises_maps_typed_nodes(ingest):
    service, transport = ingest
    res = await ingest_exercises(
        {"results": [{"id": 345, "name": "Bench Press", "category": 11}]},
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 0}
    request = transport.requests[0]
    node = next(r for r in request.records if r.record_id == "wellness:exercise:345")
    assert node.payload["name"] == "Bench Press"
    assert node.payload["externalToolId"] == "345"


@pytest.mark.asyncio
async def test_ingest_routines_maps_typed_nodes(ingest):
    service, transport = ingest
    res = await ingest_routines(
        [{"id": 42, "name": "PPL", "description": "push/pull/legs"}],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 0}
    request = transport.requests[0]
    node = next(r for r in request.records if r.record_id == "wellness:routine:42")
    assert node.payload["name"] == "PPL"


@pytest.mark.asyncio
async def test_ingest_workout_sessions_links_routine(ingest):
    service, transport = ingest
    res = await ingest_workout_sessions(
        {
            "results": [
                {"id": 9, "routine": 42, "date": "2026-07-04", "impression": "4"}
            ]
        },
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 1}
    request = transport.requests[0]
    assert any(r.record_id == "wellness:session:9" for r in request.records)
    assert request.relationships[0].relation_reference.endswith(
        "resources/WorkoutSession/relations/sessionOfRoutine"
    )


@pytest.mark.asyncio
async def test_ingest_nutrition_plans_maps_goals(ingest):
    service, transport = ingest
    res = await ingest_nutrition_plans(
        [{"id": 12, "description": "Cut", "goal_energy": 2400, "goal_protein": 180}],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 0}
    request = transport.requests[0]
    node = next(
        r for r in request.records if r.record_id == "wellness:nutritionplan:12"
    )
    assert node.payload["goalEnergy"] == 2400
    assert node.payload["goalProtein"] == 180


@pytest.mark.asyncio
async def test_retired_structural_alias_is_rejected(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError, match="node_type"):
        await ingest_entities([{"id": "a", "type": "Exercise"}], ingest=service)


@pytest.mark.asyncio
async def test_empty_native_ingest_is_rejected(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError, match="at least one entity"):
        await ingest_entities([], ingest=service)


def test_records_normalizes_wger_response_shapes():
    """Pins ``_records``'s response-shape normalisation (DRF list dict / single
    dict / plain list / None / an unrecognised type), including that non-dict
    items are filtered out of both the DRF ``results`` list and a bare list."""
    assert _records(None) == []
    assert _records({"id": 1, "name": "solo"}) == [{"id": 1, "name": "solo"}]
    assert _records({"results": [{"id": 1}, "not-a-dict", {"id": 2}]}) == [
        {"id": 1},
        {"id": 2},
    ]
    assert _records([{"id": 1}, "not-a-dict", {"id": 2}]) == [{"id": 1}, {"id": 2}]
    assert _records("unexpected-type") == []
    assert _records(42) == []
