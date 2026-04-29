"""Pytest configuration for universal-skills tests."""


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "concept(id): mark test with a concept ID for traceability",
    )
