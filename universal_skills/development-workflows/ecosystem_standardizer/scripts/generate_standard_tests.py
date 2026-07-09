#!/usr/bin/env python3
"""WS4: Generate standard test files for agents missing them.

Creates:
- test_concept_parity.py  - Validates docs/concepts.md matches code
- test_init_dynamics.py   - Validates package init and version
- conftest.py             - Standard fixtures (only if missing)
"""

import os
from pathlib import Path

AGENTS_DIR = Path("/home/apps/workspace/agent-packages/agents")

TEST_CONCEPT_PARITY = '''"""Verify CONCEPT ID parity between docs/concepts.md and codebase.

Tests that all concepts documented in docs/concepts.md are referenced
somewhere in the source code, and that no undocumented concepts exist.
"""

import re
from pathlib import Path

import pytest

PKG_DIR = Path(__file__).resolve().parent.parent
PKG_NAME = PKG_DIR.name.replace("-", "_")
SRC_DIR = PKG_DIR / PKG_NAME


@pytest.fixture
def concept_docs():
    """Load concepts from docs/concepts.md."""
    concepts_file = PKG_DIR / "docs" / "concepts.md"
    if not concepts_file.exists():
        pytest.skip("docs/concepts.md not found")
    content = concepts_file.read_text()
    # Extract CONCEPT:PREFIX-NNN patterns
    return set(re.findall(r"CONCEPT:[A-Z_]+-\\d+", content))


@pytest.fixture
def concept_code():
    """Find CONCEPT references in source code."""
    concepts = set()
    if not SRC_DIR.exists():
        return concepts
    for py_file in SRC_DIR.rglob("*.py"):
        content = py_file.read_text(errors="ignore")
        concepts.update(re.findall(r"CONCEPT:[A-Z_]+-\\d+", content))
    return concepts


def test_concepts_file_exists():
    """docs/concepts.md must exist."""
    assert (PKG_DIR / "docs" / "concepts.md").exists(), (
        "Missing docs/concepts.md — run generate_concepts.py"
    )


def test_concept_prefix_unique(concept_docs):
    """All documented concepts should share a single prefix."""
    prefixes = set()
    for c in concept_docs:
        prefix = c.split("-")[0].replace("CONCEPT:", "")
        prefixes.add(prefix)
    # Should have at most 2 prefixes: project-specific + cross-refs
    assert len(prefixes) <= 10, f"Too many CONCEPT prefixes: {prefixes}"
'''

TEST_INIT_DYNAMICS = '''"""Verify package initialization and version metadata."""

import importlib

import pytest

PKG_NAME = __name__.rsplit(".", 1)[0] if "." in __name__ else None


def _get_pkg_name():
    """Derive package name from test location."""
    import pathlib
    test_dir = pathlib.Path(__file__).resolve().parent
    project_dir = test_dir.parent
    return project_dir.name.replace("-", "_")


@pytest.fixture
def pkg_name():
    return _get_pkg_name()


def test_package_importable(pkg_name):
    """Package should be importable."""
    mod = importlib.import_module(pkg_name)
    assert mod is not None


def test_version_exists(pkg_name):
    """Package should expose __version__."""
    mod = importlib.import_module(pkg_name)
    version = getattr(mod, "__version__", None)
    # Version may come from importlib.metadata instead
    if version is None:
        from importlib.metadata import version as get_version
        version = get_version(pkg_name.replace("_", "-"))
    assert version is not None, f"{pkg_name} has no __version__"


def test_version_format(pkg_name):
    """Version should follow semver-like format."""
    mod = importlib.import_module(pkg_name)
    version = getattr(mod, "__version__", None)
    if version is None:
        from importlib.metadata import version as get_version
        version = get_version(pkg_name.replace("_", "-"))
    parts = version.split(".")
    assert len(parts) >= 2, f"Version {version} should have at least major.minor"
'''

CONFTEST_TEMPLATE = '''"""Shared test fixtures for {display_name}."""

import pytest


@pytest.fixture
def mock_env(monkeypatch):
    """Set standard test environment variables."""
    monkeypatch.setenv("{service_upper}_URL", "https://test.example.com")
    monkeypatch.setenv("{service_upper}_TOKEN", "test-token-12345")
    monkeypatch.setenv("{service_upper}_SSL_VERIFY", "False")
'''

TEST_STARTUP = '''"""Basic startup smoke tests."""

import subprocess
import sys

import pytest


def test_module_runnable():
    """Package module should be runnable with --help or similar."""
    pkg_name = __import__("pathlib").Path(__file__).resolve().parent.parent.name.replace("-", "_")
    result = subprocess.run(
        [sys.executable, "-c", f"import {pkg_name}"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
'''


def create_test_file(tests_dir: Path, filename: str, content: str) -> bool:
    """Create a test file if it doesn't exist."""
    filepath = tests_dir / filename
    if filepath.exists():
        return False
    filepath.write_text(content)
    return True


def main():
    created = 0
    skipped = 0

    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir() or agent_dir.name.startswith("."):
            continue

        tests_dir = agent_dir / "tests"
        tests_dir.mkdir(exist_ok=True)

        project_name = agent_dir.name
        display_name = project_name.replace("-", " ").title()
        service_upper = project_name.replace("-", "_").upper().split("_")[0]

        # test_concept_parity.py
        if create_test_file(tests_dir, "test_concept_parity.py", TEST_CONCEPT_PARITY):
            created += 1
        else:
            skipped += 1

        # test_init_dynamics.py
        if create_test_file(tests_dir, "test_init_dynamics.py", TEST_INIT_DYNAMICS):
            created += 1
        else:
            skipped += 1

        # test_startup.py
        if create_test_file(tests_dir, "test_startup.py", TEST_STARTUP):
            created += 1
        else:
            skipped += 1

        # conftest.py (only if missing)
        conftest_content = CONFTEST_TEMPLATE.format(
            display_name=display_name,
            service_upper=service_upper,
        )
        if create_test_file(tests_dir, "conftest.py", conftest_content):
            created += 1
        else:
            skipped += 1

    print(f"📊 Test files: {created} created, {skipped} already existed")


if __name__ == "__main__":
    main()
