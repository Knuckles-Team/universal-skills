"""Generated diagnostics and schema files preserve consumer gate boundaries."""

import ast
import importlib
import json
import sys
from pathlib import Path

import pytest
from test_mcp_builder_openapi_parity import catalog as catalog

SCRIPTS = Path(__file__).parents[1] / "universal_skills/agent-tools/mcp-builder/scripts"
sys.path.insert(0, str(SCRIPTS))


def _schema_writer():
    source = importlib.import_module("connector_templates").render_schema_generator(
        "fixture", "fixture-mcp"
    )
    tree = ast.parse(source)
    writer = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_write_or_check"
    )
    namespace = {"json": json, "Path": Path}
    exec(
        compile(ast.Module(body=[writer], type_ignores=[]), "generated_writer", "exec"),
        namespace,
    )
    return namespace




def test_parity_cli_keeps_json_rpc_stdout_empty(catalog, monkeypatch, capsys):
    _, source, package, _ = catalog
    checker = importlib.import_module("check_openapi_parity")
    monkeypatch.setattr(
        sys, "argv", ["check_openapi_parity", str(source), str(package), "--inspect"]
    )
    checker.main()
    captured = capsys.readouterr()
    assert captured.out == ""
    receipt = json.loads(captured.err)
    assert receipt["api_contract_operations"] == 8
    assert receipt["ready"] is False
