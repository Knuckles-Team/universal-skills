"""Behavioral fixtures for generated method semantics and closed action dispatch."""

import copy
import importlib
import json
import sys
from pathlib import Path

import httpx
import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)
sys.path.insert(0, str(SCRIPTS))
generate = importlib.import_module("openapi_converter").generate
compile_contract = importlib.import_module("openapi_schema").compile_contract


@pytest.fixture
def document():
    paths = {}
    for method in ("get", "post", "put", "delete", "patch", "head", "options", "trace"):
        operation = {
            "operationId": method + "Item",
            "tags": ["Items"],
            "parameters": [
                {
                    "name": "id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "minLength": 1},
                }
            ],
            "responses": {
                "200": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"ok": {"type": "boolean"}},
                                "required": ["ok"],
                            }
                        }
                    }
                }
            },
        }
        if method in {"post", "put", "patch"}:
            operation["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"count": {"type": "integer", "minimum": 1}},
                            "required": ["count"],
                            "additionalProperties": False,
                        }
                    }
                },
            }
        paths.setdefault("/items/{id}", {})[method] = operation
    return {"openapi": "3.0.3", "servers": [{"url": "/api"}], "paths": paths}


@pytest.fixture
def runtime(tmp_path, document, monkeypatch):
    pytest.importorskip("agent_connector_sdk.http.client")
    pytest.importorskip("regex")
    package = tmp_path / "fixture_connector"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps(document))
    generate(spec, package)
    monkeypatch.syspath_prepend(str(tmp_path))
    for name in list(sys.modules):
        if name == "fixture_connector" or name.startswith("fixture_connector."):
            del sys.modules[name]
    return importlib.import_module("fixture_connector.openapi_runtime")


@pytest.mark.parametrize(
    "method", ["get", "post", "put", "delete", "patch", "options", "trace"]
)
def test_exact_method_route_and_body(runtime, method):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    client = runtime.OpenApiClient(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(handler),
        allow_writes=True,
    )
    arguments = {"action": method + "Item", "path": {"id": "abc"}}
    if method in {"post", "put", "patch"}:
        arguments["body"] = {"count": 2}
    result = client.execute("items", arguments)
    assert result["data"] == {"ok": True}
    assert len(seen) == 1
    assert seen[0].method == method.upper()
    assert str(seen[0].url) == "https://provider.example/api/items/abc"
    if "body" in arguments:
        assert json.loads(seen[0].content) == arguments["body"]
    client.close()


@pytest.mark.parametrize(
    "arguments",
    [
        {"action": "unknown"},
        {"action": "getItem", "path": {"id": "../admin"}},
        {"action": "getItem", "path": {"id": "%2e%2e"}},
        {"action": "getItem", "path": {"id": "abc"}, "method": "DELETE"},
        {"action": "postItem", "path": {"id": "abc"}, "body": {"count": 0}},
    ],
)
def test_bad_input_never_requests(runtime, arguments):
    def forbidden(request):
        pytest.fail("invalid input reached provider")

    client = runtime.OpenApiClient(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(forbidden),
        allow_writes=True,
    )
    with pytest.raises(ValueError):
        client.execute("items", arguments)
    client.close()


def test_writes_disabled_by_default(runtime):
    client = runtime.OpenApiClient("https://provider.example", auth=httpx.Auth())
    with pytest.raises(PermissionError):
        client.execute("items", {"action": "deleteItem", "path": {"id": "abc"}})
    client.close()


@pytest.mark.parametrize("status", [302, 429, 500])
def test_failed_write_is_never_retried(runtime, status):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(status, headers={"location": "https://other.example/"})

    client = runtime.OpenApiClient(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(handler),
        allow_writes=True,
    )
    with pytest.raises(RuntimeError):
        client.execute("items", {"action": "deleteItem", "path": {"id": "abc"}})
    assert len(calls) == 1
    client.close()


def test_schema_is_deterministic_and_collisions_fail(document):
    first = compile_contract(document)
    reverse = copy.deepcopy(document)
    reverse["paths"]["/items/{id}"] = dict(
        reversed(list(reverse["paths"]["/items/{id}"].items()))
    )
    assert compile_contract(reverse) == first
    reverse["paths"]["/duplicate"] = copy.deepcopy(reverse["paths"]["/items/{id}"])
    with pytest.raises(ValueError, match="duplicate"):
        compile_contract(reverse)


def test_unicode_endpoint_pattern_is_preserved(runtime):
    runtime.validate("Áda", {"type": "string", "pattern": r"^\p{L}+$"})
    with pytest.raises(ValueError):
        runtime.validate("123", {"type": "string", "pattern": r"^\p{L}+$"})


def test_head_response_and_typed_output(runtime):
    operation = runtime.CONTRACT["operations"]["headItem"]
    operation["responses"] = {"204": {}}
    runtime.CONTRACT["schemas"]["items"][1]["anyOf"].append(
        {
            "type": "object",
            "properties": {
                "action": {"const": "headItem"},
                "status": {"const": 204},
                "data": {"type": "null"},
            },
            "required": ["action", "status", "data"],
        }
    )
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(204)

    client = runtime.OpenApiClient(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(handler),
    )
    assert (
        client.execute("items", {"action": "headItem", "path": {"id": "abc"}})["data"]
        is None
    )
    assert calls[0].method == "HEAD"
    client.close()


def test_response_constraints_reject_bad_provider_data(runtime):
    client = runtime.OpenApiClient(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json={"ok": "yes"})
        ),
    )
    with pytest.raises(ValueError):
        client.execute("items", {"action": "getItem", "path": {"id": "abc"}})
    client.close()


def test_auth_requirement_is_enforced_before_request(runtime):
    runtime.CONTRACT["operations"]["getItem"]["security"] = [{"api_key": []}]
    client = runtime.OpenApiClient("https://provider.example", auth=httpx.Auth())
    with pytest.raises(PermissionError):
        client.execute("items", {"action": "getItem", "path": {"id": "abc"}})
    client.close()
