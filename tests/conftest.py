"""Pytest configuration for universal-skills tests."""


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "concept(id): mark test with a concept ID for traceability",
    )

import os
import tempfile
import atexit
import shutil

_test_db_dir = tempfile.mkdtemp(prefix="universal_skills_test_db_")
os.environ["GRAPH_DB_PATH"] = os.path.join(_test_db_dir, "test_knowledge_graph.db")
os.environ["AGENT_UTILITIES_TESTING"] = "true"
