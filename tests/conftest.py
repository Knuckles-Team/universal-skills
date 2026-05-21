"""Pytest configuration for universal-skills tests."""


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "concept(id): mark test with a concept ID for traceability",
    )


import os
import pytest

os.environ["AGENT_UTILITIES_TESTING"] = "true"


@pytest.fixture(autouse=True)
def isolate_graph_db(monkeypatch, tmp_path):
    monkeypatch.setenv("GRAPH_DB_PATH", str(tmp_path / "test_knowledge_graph.db"))
    yield
