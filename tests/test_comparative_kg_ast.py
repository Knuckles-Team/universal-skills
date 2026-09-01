"""Contract coverage for comparative-analysis's native EG AST boundary."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "universal_skills/research/comparative-analysis"
SCRIPT = SKILL / "scripts/_kg_ast.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


kg_ast = _load_module("_comparative_kg_ast_test", SCRIPT)


def _native_result(node: dict | None = None) -> dict:
    return {
        "schema": "eg-native-inventory/v1",
        "producer_version": "3.0.0",
        "parser_digest": "sha256:" + "1" * 64,
        "nodes": [node] if node else [],
        "edges": [],
        "files": [],
        "symbols": [],
        "completeness": {"status": "complete"},
        "resolution_sites": [],
    }


def _install_native_client(monkeypatch, result: dict, captured: dict) -> None:
    class FakeGraph:
        def index_repository(self, files):
            captured["files"] = files
            return result

    class FakeClient:
        graph = FakeGraph()

        def __enter__(self):
            captured["entered"] = True
            return self

        def __exit__(self, *_exc):
            captured["exited"] = True

    class FakeSyncEpistemicGraphClient:
        @classmethod
        def connect(cls, **kwargs):
            captured["connect"] = kwargs
            return FakeClient()

    monkeypatch.setitem(
        sys.modules,
        "epistemic_graph",
        SimpleNamespace(SyncEpistemicGraphClient=FakeSyncEpistemicGraphClient),
    )


def test_parse_symbols_uses_strict_native_inventory_contract(monkeypatch, tmp_path):
    source = tmp_path / "sample.py"
    source.write_bytes(b"def answer():\n    return 42\n")
    expected = _native_result()
    captured: dict = {}
    _install_native_client(monkeypatch, expected, captured)
    monkeypatch.setenv("EPISTEMIC_GRAPH_TENANT", "tenant:test")
    monkeypatch.setenv("EPISTEMIC_GRAPH_POLICY_VERSION", "policy:test")

    actual = kg_ast.parse_symbols(source)

    assert actual is expected
    assert captured["files"] == [("sample.py", source.read_bytes())]
    assert captured["entered"] is True
    assert captured["exited"] is True
    connect = captured["connect"]
    assert connect["graph_name"] == "agent:comparative-analysis"
    assert connect["verified_context"] == {
        "principal": "service:comparative-analysis",
        "tenant": "tenant:test",
        "audience": "epistemic-graph",
        "agent_id": "service:comparative-analysis",
        "roles": ["graph-client"],
        "scopes": ["compute:parse"],
        "policy_version": "policy:test",
        "delegation": [],
    }


def test_parse_symbols_degrades_when_native_package_is_unavailable(
    monkeypatch, tmp_path
):
    source = tmp_path / "fallback.py"
    source.write_text('def documented():\n    """Present."""\n')
    monkeypatch.setitem(sys.modules, "epistemic_graph", None)

    result = kg_ast.parse_symbols(source)

    assert result["tier"] == "stdlib_ast_fallback"
    assert result["symbols_extracted"] == 1
    assert result["nodes"][1]["properties"]["has_docstring"] is True


def test_parse_symbols_degrades_when_native_engine_is_unavailable(
    monkeypatch, tmp_path
):
    source = tmp_path / "fallback.py"
    source.write_text("class LocalOnly:\n    pass\n")

    class UnavailableClient:
        @classmethod
        def connect(cls, **kwargs):
            raise OSError("fixture engine unavailable")

    monkeypatch.setitem(
        sys.modules,
        "epistemic_graph",
        SimpleNamespace(SyncEpistemicGraphClient=UnavailableClient),
    )

    result = kg_ast.parse_symbols(source)

    assert result["tier"] == "stdlib_ast_fallback"
    assert result["nodes"][1]["properties"]["name"] == "LocalOnly"


def test_documentation_analyzer_reaches_native_inventory(monkeypatch, tmp_path):
    source = tmp_path / "documented.py"
    source.write_text('def documented():\n    """Present."""\n')
    node = {
        "node_id": "symbol:documented",
        "node_type": "SYMBOL",
        "properties": {
            "name": "documented",
            "symbol_type": "Function",
            "line": "1",
        },
    }
    captured: dict = {}
    _install_native_client(monkeypatch, _native_result(node), captured)
    monkeypatch.setitem(sys.modules, "_kg_ast", kg_ast)
    analyzer = _load_module(
        "_comparative_documentation_test", SKILL / "scripts/analyze_documentation.py"
    )

    result = analyzer.analyze_docstrings(tmp_path)

    assert result == {
        "total_definitions": 1,
        "documented": 1,
        "coverage_pct": 100.0,
    }
    assert captured["files"] == [("documented.py", source.read_bytes())]


def test_legacy_parser_import_is_gone():
    assert "from epistemic_graph.parser" not in SCRIPT.read_text()
