"""US-WEB-RESEARCH-R002: skills read the graph through the served arbora surface only."""

from __future__ import annotations

import pytest

from universal_skills import _arbora


@pytest.mark.spec("US-WEB-RESEARCH-R002")
def test_graph_calls_return_none_without_a_gateway(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARBORA_URL", raising=False)
    assert _arbora.graph_query("MATCH (n) RETURN n") is None
    assert _arbora.graph_search("anything") is None


@pytest.mark.spec("US-WEB-RESEARCH-R002")
def test_graph_query_posts_to_the_query_twin_and_unwraps_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}

    def fake_open_json(request, *, policy, timeout, max_bytes):
        seen["url"] = request.full_url
        seen["auth"] = request.get_header("Authorization")
        return {"status": "success", "result": {"rows": [{"id": 1}, "skip"]}}, None

    monkeypatch.setenv("ARBORA_URL", "http://127.0.0.1:8000/")
    monkeypatch.setenv("ARBORA_TOKEN", "t0ken")
    monkeypatch.setattr(_arbora, "open_json", fake_open_json)
    assert _arbora.graph_query("MATCH (n) RETURN n") == [{"id": 1}]
    assert seen == {
        "url": "http://127.0.0.1:8000/api/graph/query",
        "auth": "Bearer t0ken",
    }


@pytest.mark.spec("US-WEB-RESEARCH-R002")
def test_a_failed_response_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARBORA_URL", "http://127.0.0.1:8000")
    monkeypatch.setattr(
        _arbora, "open_json", lambda *a, **k: ({"status": "error"}, None)
    )
    assert _arbora.graph_search("q") is None
