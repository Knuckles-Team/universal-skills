"""Comprehensive test suite for code-enhancer skill scripts.

Tests all new and enhanced analysis domains (CE-015 through CE-021 plus
CE-008 enhancements). Each test is tagged with concept markers for
traceability.

CONCEPT:CE-TEST — Code Enhancer Test Suite
"""

import json
import os
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers: create temporary project structures
# ---------------------------------------------------------------------------

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / (
    "universal_skills/core/code-enhancer/scripts"
)


def _import_script(name: str):
    """Import a code-enhancer script module by name."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, str(SCRIPTS_DIR / f"{name}.py"))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_python_project(
    tmp_path: Path,
    *,
    with_tests: bool = True,
    with_precommit: bool = False,
    with_pyproject: bool = True,
    extra_files: dict | None = None,
) -> Path:
    """Create a minimal Python project scaffold."""
    root = tmp_path / "project"
    root.mkdir()
    if with_pyproject:
        (root / "pyproject.toml").write_text(
            textwrap.dedent("""\
            [project]
            name = "test-project"
            version = "0.1.0"
            dependencies = ["pydantic-ai>=0.1", "pytest>=8.0"]
        """)
        )
    if with_tests:
        tests = root / "tests"
        tests.mkdir()
        (tests / "test_example.py").write_text(
            textwrap.dedent("""\
            import pytest

            @pytest.mark.concept("TP-001")
            def test_hello():
                assert True

            def test_no_concept():
                assert 1 + 1 == 2
        """)
        )
    if with_precommit:
        (root / ".pre-commit-config.yaml").write_text(
            textwrap.dedent("""\
            repos:
              - repo: https://github.com/astral-sh/ruff-pre-commit
                rev: v0.4.0
                hooks:
                  - id: ruff
              - repo: local
                hooks:
                  - id: pytest
                    name: pytest
                    entry: pytest
                    language: system
                    types: [python]
        """)
        )
    # Source files
    src = root / "src"
    src.mkdir()
    (src / "__init__.py").write_text("")
    (src / "main.py").write_text(
        textwrap.dedent("""\
        \"\"\"Main module.

        CONCEPT:TP-001 — Test Project Core
        \"\"\"

        def hello():
            \"\"\"Say hello.\"\"\"
            return "hello"

        def complex_function():
            \"\"\"A longer function for testing.

            CONCEPT:TP-002 — Complex Logic
            \"\"\"
            result = 0
            for i in range(100):
                if i % 2 == 0:
                    if i % 3 == 0:
                        if i % 5 == 0:
                            result += i
                        else:
                            result -= 1
                    else:
                        result += 2
                else:
                    result -= 1
            return result
    """)
    )
    # Docs
    (root / "README.md").write_text(
        textwrap.dedent("""\
        # Test Project

        A test project for code-enhancer.

        ## Installation

        ```bash
        pip install test-project
        ```

        ## Usage

        ```python
        from src import main
        main.hello()
        ```

        CONCEPT:TP-001 — documented in README
    """)
    )
    (root / "AGENTS.md").write_text(
        textwrap.dedent("""\
        # AGENTS

        ## Tech Stack
        - Python 3.13

        ## Commands
        - `pytest`

        ## Project Structure
        - src/ — source code

        <!-- CONCEPT:TP-001 -->
        <!-- CONCEPT:TP-002 -->
        <!-- CONCEPT:TP-003 -->
    """)
    )

    if extra_files:
        for name, content in extra_files.items():
            fpath = root / name
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content)

    return root


# ═══════════════════════════════════════════════════════════════════════
# CE-018: Language Detection
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.concept("CE-018")
class TestDetectLanguage:
    """Test language ecosystem detection."""

    def test_detect_python(self, tmp_path: Path):
        root = _make_python_project(tmp_path)
        mod = _import_script("detect_language")
        result = mod.detect_language(str(root))
        assert result["primary_language"] == "python"
        assert "pyproject" in result["build_systems"]

    def test_detect_go(self, tmp_path: Path):
        root = tmp_path / "goproject"
        root.mkdir()
        (root / "go.mod").write_text("module example.com/test\n\ngo 1.21\n")
        (root / "main.go").write_text("package main\n\nfunc main() {}\n")
        mod = _import_script("detect_language")
        result = mod.detect_language(str(root))
        assert result["primary_language"] == "go"

    def test_detect_node(self, tmp_path: Path):
        root = tmp_path / "nodeproject"
        root.mkdir()
        (root / "package.json").write_text(
            json.dumps(
                {
                    "name": "test",
                    "scripts": {"test": "jest"},
                    "dependencies": {"react": "^18.0"},
                }
            )
        )
        (root / "index.js").write_text("console.log('hello');\n")
        mod = _import_script("detect_language")
        result = mod.detect_language(str(root))
        assert result["primary_language"] in ("node", "web")

    def test_detect_java(self, tmp_path: Path):
        root = tmp_path / "javaproject"
        root.mkdir()
        (root / "pom.xml").write_text("<project></project>")
        (root / "src").mkdir()
        (root / "src" / "Main.java").write_text("class Main {}")
        mod = _import_script("detect_language")
        result = mod.detect_language(str(root))
        assert result["primary_language"] == "java"

    def test_detect_unknown(self, tmp_path: Path):
        root = tmp_path / "empty"
        root.mkdir()
        mod = _import_script("detect_language")
        result = mod.detect_language(str(root))
        assert result["primary_language"] == "unknown"


# ═══════════════════════════════════════════════════════════════════════
# CE-015: Pre-Commit Compliance
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.concept("CE-015")
class TestRunPrecommit:
    """Test pre-commit compliance analysis."""

    def test_no_config(self, tmp_path: Path):
        root = tmp_path / "noconfig"
        root.mkdir()
        mod = _import_script("run_precommit")
        result = mod.run_precommit(str(root))
        assert result["score"] == 15
        assert result["grade"] == "F"
        assert "No .pre-commit-config" in result["findings"][0]

    def test_detect_pytest_hooks(self, tmp_path: Path):
        root = _make_python_project(tmp_path, with_precommit=True)
        mod = _import_script("run_precommit")
        hooks = mod._detect_pytest_hooks_in_config(root / ".pre-commit-config.yaml")
        assert "pytest" in hooks

    def test_outdated_hook_detection(self, tmp_path: Path):
        root = tmp_path / "outdated"
        root.mkdir()
        (root / ".pre-commit-config.yaml").write_text(
            textwrap.dedent("""\
            repos:
              - repo: https://github.com/example/hook
                rev: abc123def456abc123def456abc123def456abc1
                hooks:
                  - id: example-hook
        """)
        )
        mod = _import_script("run_precommit")
        outdated = mod._detect_outdated_hooks(root / ".pre-commit-config.yaml")
        assert len(outdated) == 1
        assert (
            "hash" in outdated[0]["issue"].lower()
            or "pinned" in outdated[0]["issue"].lower()
        )

    def test_pre_commit_not_installed(self, tmp_path: Path):
        root = _make_python_project(tmp_path, with_precommit=True)
        mod = _import_script("run_precommit")
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = mod.run_precommit(str(root))
        assert result["score"] == 30
        assert "not installed" in result["findings"][0]

    def test_pre_commit_timeout(self, tmp_path: Path):
        root = _make_python_project(tmp_path, with_precommit=True)
        mod = _import_script("run_precommit")
        import subprocess

        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="pre-commit", timeout=300),
        ):
            result = mod.run_precommit(str(root))
        assert result["score"] == 40
        assert "timed out" in result["findings"][0]


# ═══════════════════════════════════════════════════════════════════════
# CE-016: Test Execution
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.concept("CE-016")
class TestRunTests:
    """Test execution and grading."""

    def test_no_framework_detected(self, tmp_path: Path):
        root = tmp_path / "noproj"
        root.mkdir()
        mod = _import_script("run_tests")
        result = mod.run_tests(str(root))
        assert result["score"] == 20
        assert result["grade"] == "F"

    def test_detect_pytest_framework(self, tmp_path: Path):
        root = _make_python_project(tmp_path)
        mod = _import_script("run_tests")
        frameworks = mod._detect_test_framework(root)
        assert len(frameworks) >= 1
        assert frameworks[0]["framework"] == "pytest"

    def test_detect_go_framework(self, tmp_path: Path):
        root = tmp_path / "gotest"
        root.mkdir()
        (root / "go.mod").write_text("module test\ngo 1.21\n")
        mod = _import_script("run_tests")
        frameworks = mod._detect_test_framework(root)
        assert any(f["framework"] == "go test" for f in frameworks)

    def test_detect_node_framework(self, tmp_path: Path):
        root = tmp_path / "nodetest"
        root.mkdir()
        (root / "package.json").write_text(
            json.dumps({"name": "test", "scripts": {"test": "jest"}})
        )
        mod = _import_script("run_tests")
        frameworks = mod._detect_test_framework(root)
        assert any(f["framework"] == "jest" for f in frameworks)

    def test_parse_pytest_output_pass(self):
        mod = _import_script("run_tests")
        result = mod._parse_pytest_output("10 passed in 1.23s", "")
        assert result["passed"] == 10
        assert result["failed"] == 0

    def test_parse_pytest_output_fail(self):
        mod = _import_script("run_tests")
        result = mod._parse_pytest_output(
            "8 passed, 2 failed in 5.00s\nFAILED tests/test_a.py::test_one\nFAILED tests/test_b.py::test_two",
            "",
        )
        assert result["passed"] == 8
        assert result["failed"] == 2
        assert len(result["failures"]) == 2


# ═══════════════════════════════════════════════════════════════════════
# CE-017: Directory Organization
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.concept("CE-017")
class TestDirectoryDensity:
    """Test directory organization analysis."""

    def test_normal_project(self, tmp_path: Path):
        root = _make_python_project(tmp_path)
        mod = _import_script("analyze_directory_density")
        result = mod.analyze_directory_density(str(root))
        assert result["grade"] in ("A", "B")
        assert result["metrics"]["crowded_dirs_20plus"] == 0

    def test_crowded_directory(self, tmp_path: Path):
        root = tmp_path / "crowded"
        root.mkdir()
        pkg = root / "pkg"
        pkg.mkdir()
        for i in range(30):
            (pkg / f"module_{i}.py").write_text(f"# module {i}\n")
        mod = _import_script("analyze_directory_density")
        result = mod.analyze_directory_density(str(root))
        assert result["metrics"]["crowded_dirs_20plus"] >= 1
        assert any("crowded" in f.lower() or ">20" in f for f in result["findings"])

    def test_flat_project(self, tmp_path: Path):
        root = tmp_path / "flat"
        root.mkdir()
        for i in range(25):
            (root / f"file_{i}.py").write_text(f"x = {i}\n")
        mod = _import_script("analyze_directory_density")
        result = mod.analyze_directory_density(str(root))
        # Should detect flat structure
        assert result["metrics"]["max_depth"] <= 1

    def test_deep_project(self, tmp_path: Path):
        root = tmp_path / "deep"
        current = root
        for i in range(10):
            current = current / f"level_{i}"
            current.mkdir(parents=True, exist_ok=True)
        (current / "deep_file.py").write_text("x = 1\n")
        mod = _import_script("analyze_directory_density")
        result = mod.analyze_directory_density(str(root))
        assert result["metrics"]["max_depth"] >= 8


# ═══════════════════════════════════════════════════════════════════════
# CE-019: UI/UX Quality
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.concept("CE-019")
class TestAnalyzeUI:
    """Test UI/UX heuristic analysis."""

    def test_no_ui_detected(self, tmp_path: Path):
        root = _make_python_project(tmp_path)
        mod = _import_script("analyze_ui")
        result = mod.analyze_ui(str(root))
        assert result["score"] == -1
        assert result["grade"] == "N/A"
        assert result["ui_type"] is None

    def test_web_ui_detection(self, tmp_path: Path):
        root = tmp_path / "webapp"
        root.mkdir()
        (root / "package.json").write_text(
            json.dumps({"dependencies": {"react": "^18.0"}})
        )
        src = root / "src"
        src.mkdir()
        (src / "App.tsx").write_text(
            textwrap.dedent("""\
            import React from 'react';
            export default function App() {
                return (
                    <nav aria-label="main">
                        <main>
                            <section>
                                <article>Content</article>
                            </section>
                        </main>
                    </nav>
                );
            }
        """)
        )
        mod = _import_script("analyze_ui")
        result = mod.analyze_ui(str(root))
        assert result["ui_type"] == "web"
        assert result["score"] >= 0

    def test_terminal_ui_detection(self, tmp_path: Path):
        root = tmp_path / "tuiapp"
        root.mkdir()
        (root / "pyproject.toml").write_text(
            textwrap.dedent("""\
            [project]
            name = "tui-app"
            dependencies = ["textual>=0.40"]
        """)
        )
        (root / "app.py").write_text(
            textwrap.dedent("""\
            from textual.app import App
            from textual.widgets import Header, Footer
            import sys

            class MyApp(App):
                BINDINGS = [("q", "quit", "Quit")]
                CSS = "Screen { background: blue; }"

                def compose(self):
                    yield Header()
                    yield Footer()

            if __name__ == "__main__":
                try:
                    MyApp().run()
                except KeyboardInterrupt:
                    sys.exit(0)
        """)
        )
        mod = _import_script("analyze_ui")
        result = mod.analyze_ui(str(root))
        assert result["ui_type"] == "terminal"
        assert result["score"] >= 0

    def test_heuristic_count(self):
        mod = _import_script("analyze_ui")
        assert len(mod.HEURISTICS) == 10

    def test_web_accessibility_checks(self, tmp_path: Path):
        root = tmp_path / "a11y"
        root.mkdir()
        (root / "index.html").write_text(
            textwrap.dedent("""\
            <html lang="en">
            <body>
                <img src="test.jpg" alt="A test image">
                <button aria-label="Submit" role="button" tabindex="0">Go</button>
            </body>
            </html>
        """)
        )
        # Need enough HTML files to trigger web detection
        for i in range(6):
            (root / f"page{i}.html").write_text(f"<html><body>Page {i}</body></html>")
        mod = _import_script("analyze_ui")
        result = mod.analyze_ui(str(root))
        if result["ui_type"] == "web":
            a11y = result["accessibility"]
            assert a11y["alt_tags"] is True
            assert a11y["aria_labels"] is True


# ═══════════════════════════════════════════════════════════════════════
# CE-021: Cross-Project Integration
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.concept("CE-021")
class TestAnalyzeIntegration:
    """Test cross-project integration analysis."""

    def test_single_project_skipped(self, tmp_path: Path):
        root = _make_python_project(tmp_path)
        mod = _import_script("analyze_integration")
        result = mod.analyze_integration([str(root)])
        assert result["score"] == -1
        assert result["grade"] == "N/A"

    def test_dependency_graph(self, tmp_path: Path):
        # Project A depends on Project B
        a = tmp_path / "proj_a"
        a.mkdir()
        (a / "pyproject.toml").write_text(
            textwrap.dedent("""\
            [project]
            name = "proj-a"
            dependencies = ["proj-b>=1.0"]
        """)
        )
        b = tmp_path / "proj_b"
        b.mkdir()
        (b / "pyproject.toml").write_text(
            textwrap.dedent("""\
            [project]
            name = "proj-b"
            dependencies = ["requests>=2.0"]
        """)
        )
        mod = _import_script("analyze_integration")
        result = mod.analyze_integration([str(a), str(b)])
        assert "proj_a" in result["dependency_graph"]
        assert "proj_b" in result["dependency_graph"]["proj_a"]

    def test_version_conflicts(self, tmp_path: Path):
        a = tmp_path / "conflict_a"
        a.mkdir()
        (a / "pyproject.toml").write_text(
            textwrap.dedent("""\
            [project]
            name = "conflict-a"
            dependencies = ["pydantic>=2.0"]
        """)
        )
        b = tmp_path / "conflict_b"
        b.mkdir()
        (b / "pyproject.toml").write_text(
            textwrap.dedent("""\
            [project]
            name = "conflict-b"
            dependencies = ["pydantic>=1.0,<2.0"]
        """)
        )
        mod = _import_script("analyze_integration")
        result = mod.analyze_integration([str(a), str(b)])
        assert len(result["conflicts"]) >= 1
        assert result["score"] < 100

    def test_circular_dependencies(self, tmp_path: Path):
        a = tmp_path / "circ_a"
        a.mkdir()
        (a / "pyproject.toml").write_text(
            textwrap.dedent("""\
            [project]
            name = "circ-a"
            dependencies = ["circ-b>=1.0"]
        """)
        )
        b = tmp_path / "circ_b"
        b.mkdir()
        (b / "pyproject.toml").write_text(
            textwrap.dedent("""\
            [project]
            name = "circ-b"
            dependencies = ["circ-a>=1.0"]
        """)
        )
        mod = _import_script("analyze_integration")
        result = mod.analyze_integration([str(a), str(b)])
        assert len(result["circular_deps"]) >= 1


# ═══════════════════════════════════════════════════════════════════════
# CE-020: Multi-Project Orchestration
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.concept("CE-020")
class TestMultiProject:
    """Test multi-project orchestration."""

    def test_discover_projects(self, tmp_path: Path):
        # Create two projects
        for name in ("proj1", "proj2"):
            d = tmp_path / name
            d.mkdir()
            (d / "pyproject.toml").write_text(f'[project]\nname = "{name}"\n')
        mod = _import_script("run_multi_project")
        projects = mod._discover_projects(str(tmp_path))
        assert len(projects) == 2

    def test_discover_non_projects(self, tmp_path: Path):
        # Directory without pyproject.toml
        d = tmp_path / "notaproject"
        d.mkdir()
        (d / "readme.txt").write_text("not a project")
        mod = _import_script("run_multi_project")
        projects = mod._discover_projects(str(d))
        assert len(projects) == 0

    def test_run_single_project(self, tmp_path: Path):
        root = _make_python_project(tmp_path)
        mod = _import_script("run_multi_project")
        result = mod._run_single_project(str(root))
        assert result["project"] == root.name
        assert result["gpa"] >= 0
        assert len(result["domain_results"]) > 0


# ═══════════════════════════════════════════════════════════════════════
# CE-008: Enhanced Concept Traceability
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.concept("CE-008")
class TestTraceConceptsEnhanced:
    """Test enhanced concept traceability."""

    def test_decorator_detection(self, tmp_path: Path):
        root = _make_python_project(tmp_path)
        mod = _import_script("trace_concepts")
        concepts, missing = mod._scan_pytest_decorators(root)
        # Should find the @pytest.mark.concept("TP-001") decorator
        assert any(c["concept_id"] == "TP-001" for c in concepts)

    def test_missing_markers_detected(self, tmp_path: Path):
        root = _make_python_project(tmp_path)
        mod = _import_script("trace_concepts")
        _, missing = mod._scan_pytest_decorators(root)
        # test_no_concept() should be in missing
        assert any(m["test_name"] == "test_no_concept" for m in missing)

    def test_registry_cross_reference(self, tmp_path: Path):
        root = _make_python_project(tmp_path)
        mod = _import_script("trace_concepts")
        registry = mod._load_concept_registry(root)
        assert "TP-001" in registry
        assert "TP-003" in registry  # In AGENTS.md but not in code

    def test_full_trace_run(self, tmp_path: Path):
        root = _make_python_project(tmp_path)
        mod = _import_script("trace_concepts")
        result = mod.trace_concepts(str(root))
        assert result["domain"] == "Concept Traceability"
        assert result["metrics"]["total_concepts"] > 0
        assert "tests_missing_markers" in result
        # TP-003 is in AGENTS.md docs but not in code → should be an orphan
        assert "TP-003" in result["concept_map"]
        tp3 = result["concept_map"]["TP-003"]
        assert tp3["docs"] > 0
        assert tp3["code"] == 0
