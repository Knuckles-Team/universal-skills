"""Pytest configuration for universal-skills tests."""

import os
import importlib

import pytest


os.environ["AGENT_UTILITIES_TESTING"] = "true"


def pytest_configure(config):
    """Register markers and fail closed for the dedicated SDK contract job."""
    if os.environ.get("MCP_BUILDER_REQUIRE_SDK") == "1":
        # The required CI job must never turn missing SDK dependencies into skips.
        importlib.import_module("scion_sdk.mcp.server")
        importlib.import_module("scion_sdk.ingest")
    config.addinivalue_line(
        "markers",
        "concept(id): mark test with a concept ID for traceability",
    )


@pytest.fixture(autouse=True)
def isolate_graph_db(monkeypatch, tmp_path):
    monkeypatch.setenv("GRAPH_DB_PATH", str(tmp_path / "test_knowledge_graph.db"))
    yield
