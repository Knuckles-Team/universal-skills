"""Native deferred discovery keeps exact schemas, reachability and strict budgets."""

import asyncio
import importlib
import json
import sys
from pathlib import Path

import pytest
from test_mcp_builder_openapi_parity import catalog as catalog

SCRIPTS = Path(__file__).parents[1] / "universal_skills/skills/mcp-builder/scripts"
sys.path.insert(0, str(SCRIPTS))
budgets = importlib.import_module("openapi_schema_budget")
discovery = importlib.import_module("openapi_discovery")


def test_ready_claim_requires_named_native_budget(catalog, budget, monkeypatch):
    pytest.importorskip("agent_connector_sdk")
    document, source, package, _ = catalog
    document["security"] = []
    source.write_text(json.dumps(document))
    importlib.import_module("openapi_converter").generate(source, package)
    (package / "__init__.py").write_text("")
    (package / "mcp_server.py").write_text(
        "from fastmcp import FastMCP\n"
        "from .openapi_runtime import register_domain\n"
        "def build_server(command_args=None):\n"
        "    server = FastMCP('readiness')\n"
        "    register_domain(server, 'items', lambda: None)\n"
        "    return server\n"
    )
    monkeypatch.syspath_prepend(str(package.parent))
    for name in list(sys.modules):
        if name == package.name or name.startswith(package.name + "."):
            del sys.modules[name]
    checker = importlib.import_module("check_openapi_parity")
    with pytest.raises(ValueError, match="explicit named client budget"):
        checker.check(source, package, native=True)
    assert checker.check(source, package, mode="inspect")["ready"] is False
    with pytest.raises(ValueError, match="active in the normal runtime"):
        checker.check(source, package, native=True, client_budget=budget)
    budget_path = package.parent / "client-budget.json"
    budget_path.write_text(json.dumps(budget))
    monkeypatch.setenv(package.name.upper() + "_MCP_CLIENT_BUDGET", str(budget_path))
    receipt = checker.check(source, package, native=True, client_budget=budget)
    assert receipt["ready"] is True
    assert receipt["native_mcp"]["exposed_operations"] == 8
    assert (
        receipt["disclosure"]["retrievals"]["get_items"]["client"]
        == budget["client"]
    )
    with pytest.raises(Exception, match="Schema budget exceeded"):
        budget_path.write_text(json.dumps({**budget, "max_output_schema_bytes": 1}))
        checker.check(
            source,
            package,
            native=True,
            client_budget={**budget, "max_output_schema_bytes": 1},
        )


def test_checker_restores_same_named_imports_and_path(tmp_path):
    from types import ModuleType

    checker = importlib.import_module("check_openapi_parity")
    package = tmp_path / "collision_fixture"
    package.mkdir()
    (package / "__init__.py").write_text("origin = 'requested'\n")
    old = ModuleType(package.name)
    old.origin = "cached"
    sys.modules[package.name] = old
    before = list(sys.path)
    try:
        with pytest.raises(RuntimeError, match="test cleanup"):
            with checker.project_imports(package):
                assert importlib.import_module(package.name).origin == "requested"
                raise RuntimeError("test cleanup")
        assert sys.modules[package.name] is old
        assert sys.path == before
    finally:
        sys.modules.pop(package.name)


@pytest.fixture
def budget():
    return {
        "version": 1,
        "client": "explicit-local-fixture",
        "discovery": "regex-search",
        **{name: 32_000 for name in budgets.LIMITS},
    }


@pytest.mark.parametrize(
    "bad",
    [
        None,
        {},
        {"client": ""},
        {"max_tool_bytes": True},
        {"discovery": "truncate"},
        {"max_listing_bytes": 0},
    ],
)
def test_budget_is_explicit_and_named(budget, bad):
    value = bad if bad is None or bad == {} else {**budget, **bad}
    with pytest.raises(ValueError):
        budgets.client_budget(value)


@pytest.mark.parametrize("key", budgets.LIMITS)
def test_each_budget_is_enforced(budget, key):
    pytest.importorskip("fastmcp")
    budget[key] = 1
    tool = {
        "name": "item",
        "inputSchema": {"type": "object"},
        "outputSchema": {"type": "object"},
    }
    with pytest.raises(ValueError, match="budget exceeded"):
        budgets.require_schema_budget(
            [tool],
            budget,
            kind="search_result" if key == "max_search_result_bytes" else "listing",
        )


def test_expanded_refs_cannot_hide_oversize(budget):
    pytest.importorskip("fastmcp")
    budget["max_input_schema_bytes"] = 300
    tool = {
        "name": "item",
        "inputSchema": {
            "type": "object",
            "properties": {str(n): {"$ref": "#/$defs/text"} for n in range(8)},
            "$defs": {"text": {"type": "string", "pattern": "a" * 70}},
        },
    }
    with pytest.raises(ValueError, match="input_schema_bytes"):
        budgets.require_schema_budget([tool], budget)


def test_reference_and_sibling_assertions_remain_an_intersection():
    pytest.importorskip("fastmcp")
    from fastmcp.utilities.json_schema import dereference_refs
    from jsonschema import Draft202012Validator

    translate = importlib.import_module("openapi_schema_types").schema
    source = {"$ref": "#/components/schemas/Code", "minLength": 1}
    compiled = translate(source)
    compiled["$defs"] = {"Code": {"type": "string", "minLength": 10}}
    served = dereference_refs(compiled)
    for value in (compiled, served):
        validator = Draft202012Validator(value)
        assert not validator.is_valid("short")
        assert validator.is_valid("long enough")


@pytest.mark.parametrize(
    "definition, keyword, accepted, rejected",
    [
        (
            {"type": "object", "properties": {"a": {"type": "string"}}},
            "unevaluatedProperties",
            {"a": "ok"},
            {"a": "ok", "b": "no"},
        ),
        (
            {"type": "array", "prefixItems": [{"type": "string"}]},
            "unevaluatedItems",
            ["ok"],
            ["ok", "no"],
        ),
    ],
)
def test_reference_siblings_keep_annotation_scope(
    definition, keyword, accepted, rejected
):
    pytest.importorskip("fastmcp")
    from fastmcp.utilities.json_schema import dereference_refs
    from jsonschema import Draft202012Validator

    translate = importlib.import_module("openapi_schema_types").schema
    source = {"$ref": "#/components/schemas/Value", keyword: False, "allOf": [{}]}
    compiled = translate(source)
    assert len(compiled["allOf"]) == 2
    compiled["$defs"] = {"Value": definition}
    for value in (compiled, dereference_refs(compiled)):
        validator = Draft202012Validator(value)
        assert validator.is_valid(accepted)
        assert not validator.is_valid(rejected)


def test_native_eager_listing_enforces_aggregate_budget(budget):
    fastmcp = pytest.importorskip("fastmcp")
    server = fastmcp.FastMCP("Oversize eager fixture")

    @server.tool(description="x" * 40_000)
    def oversized(value: int) -> int:
        return value

    discovery.configure_discovery(server, {**budget, "discovery": "eager"})

    async def run():
        async with fastmcp.Client(server) as client:
            with pytest.raises(Exception, match="Schema budget exceeded"):
                await client.list_tools()

    asyncio.run(run())


def test_native_search_preserves_schema_and_direct_calls(budget):
    fastmcp = pytest.importorskip("fastmcp")
    server = fastmcp.FastMCP("Bounded native fixture")
    calls = []

    @server.tool
    def first(value: int) -> int:
        calls.append(value)
        return value + 1

    @server.tool
    def second(value: str) -> str:
        return value.upper()

    async def run():
        async with fastmcp.Client(server) as client:
            original = await client.list_tools()
        discovery.configure_discovery(server, budget)
        discovery.configure_discovery(server, budget)
        async with fastmcp.Client(server) as client:
            listed = await client.list_tools()
            assert {tool.name for tool in listed} == {"search_tools", "call_tool"}
            budgets.require_schema_budget(listed, budget)
            for tool in original:
                result = await client.call_tool(
                    "search_tools", {"pattern": "^" + tool.name + r"(?:\s|$)"}
                )
                actual = result.data
                if isinstance(actual, dict):
                    actual = actual["result"]
                assert actual == [budgets.wire_tool(tool)]
                budgets.require_schema_budget(actual, budget, kind="search_result")
            assert (await client.call_tool("first", {"value": 2})).data == 3
            assert (
                await client.call_tool(
                    "call_tool", {"name": "second", "arguments": {"value": "ok"}}
                )
            ).data == "OK"
            with pytest.raises(Exception, match="validation|integer|valid"):
                await client.call_tool("first", {"value": "invalid"})
        assert calls == [2]

    asyncio.run(run())


def test_native_oversized_schema_is_refused_without_truncation(budget):
    fastmcp = pytest.importorskip("fastmcp")
    server = fastmcp.FastMCP("Oversize fixture")

    @server.tool(description="x" * 40_000)
    def oversized(value: int) -> int:
        return value

    discovery.configure_discovery(server, budget)

    async def run():
        async with fastmcp.Client(server) as client:
            assert len(await client.list_tools()) == 2
            with pytest.raises(Exception, match="Schema budget exceeded"):
                await client.call_tool("search_tools", {"pattern": "^oversized"})
            assert (await client.call_tool("oversized", {"value": 1})).data == 1

    asyncio.run(run())


def test_budget_file_changes_cannot_replace_an_active_policy(budget, tmp_path):
    fastmcp = pytest.importorskip("fastmcp")
    server = fastmcp.FastMCP("Fixed policy")
    path = tmp_path / "budget.json"
    path.write_text(json.dumps(budget))
    discovery.configure_discovery(server, path)
    with pytest.raises(ValueError, match="Cannot replace"):
        discovery.configure_discovery(server, {**budget, "max_tool_bytes": 64_000})
