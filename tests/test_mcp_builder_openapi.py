"""Behavioral fixtures for generated method semantics and closed action dispatch."""

import asyncio
import copy
import importlib
import json
import os
import ssl
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


def parity_name(action):
    import re

    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", action)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def _require_runtime():
    for name in ("agent_connector_sdk.http.client", "regex"):
        if os.environ.get("MCP_BUILDER_REQUIRE_SDK") == "1":
            importlib.import_module(name)
        else:
            pytest.importorskip(name)


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
    return {
        "openapi": "3.0.3",
        "security": [],
        "servers": [{"url": "/api"}],
        "paths": paths,
    }


@pytest.fixture
def runtime(tmp_path, document, monkeypatch):
    _require_runtime()
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

    client = runtime.OpenApiClientBase(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(handler),
        write_mode="read-write",
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

    client = runtime.OpenApiClientBase(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(forbidden),
        write_mode="read-write",
    )
    with pytest.raises(ValueError):
        client.execute("items", arguments)
    client.close()


def test_writes_disabled_by_default(runtime):
    client = runtime.OpenApiClientBase("https://provider.example", auth=httpx.Auth())
    with pytest.raises(PermissionError):
        client.execute("items", {"action": "deleteItem", "path": {"id": "abc"}})
    client.close()


@pytest.mark.parametrize("decision", ["pending", True, False, None, "truthy"])
def test_tool_confirmation_result_never_dispatches_until_exact_true(
    runtime, monkeypatch, decision
):
    from mcp.types import InputRequiredResult

    requests = []
    client = runtime.OpenApiClientBase(
        "https://provider.example",
        auth=httpx.Auth(),
        write_mode="read-write",
        transport=httpx.MockTransport(
            lambda request: (
                requests.append(request) or httpx.Response(200, json={"ok": True})
            )
        ),
    )
    arguments = {"path": {"id": "one"}}
    pending = InputRequiredResult(request_state="test-state")

    async def confirm(context, action, *, confirmation_arguments):
        assert action == "deleteItem"
        assert confirmation_arguments == {"action": "deleteItem", **arguments}
        return pending if decision == "pending" else decision

    execution = importlib.import_module(runtime.__package__ + ".openapi_execution")
    monkeypatch.setattr(execution, "ctx_confirm_destructive", confirm)
    monkeypatch.setattr(execution, "get_context", lambda: object())
    tool = runtime.OpenApiTool(
        name=runtime.operation_tool_name("deleteItem"),
        domain="items",
        action="deleteItem",
        client_factory=lambda: client,
        parameters=runtime.operation_input_schema("deleteItem"),
        output_schema=runtime.CONTRACT["schemas"]["items"][1],
    )
    try:
        if decision == "pending":
            assert asyncio.run(tool.run(arguments)) is pending
        elif decision is True:
            assert asyncio.run(tool.run(arguments)).structured_content["data"] == {
                "ok": True
            }
        else:
            with pytest.raises(PermissionError, match="not confirmed"):
                asyncio.run(tool.run(arguments))
        assert len(requests) == (1 if decision is True else 0)
    finally:
        client.close()


@pytest.mark.parametrize("status", [302, 429, 500])
def test_failed_write_is_never_retried(runtime, status):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(status, headers={"location": "https://other.example/"})

    client = runtime.OpenApiClientBase(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(handler),
        write_mode="read-write",
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

    client = runtime.OpenApiClientBase(
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
    client = runtime.OpenApiClientBase(
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
    client = runtime.OpenApiClientBase("https://provider.example", auth=httpx.Auth())
    with pytest.raises(PermissionError):
        client.execute("items", {"action": "getItem", "path": {"id": "abc"}})
    client.close()


def test_plaintext_requires_explicit_endpoint_opt_in(runtime):
    with pytest.raises(ValueError, match="allow_plaintext"):
        runtime.OpenApiClientBase("http://provider.example", auth=httpx.Auth())
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    client = runtime.OpenApiClientBase(
        "http://provider.example",
        auth=httpx.Auth(),
        allow_plaintext=True,
        transport=httpx.MockTransport(handler),
    )
    client.execute("items", {"action": "getItem", "path": {"id": "abc"}})
    assert str(seen[0].url) == "http://provider.example/api/items/abc"
    client.close()


@pytest.mark.parametrize(
    "location",
    [
        "https://other.example/leak",
        "http://provider.example/downgrade",
    ],
)
def test_credentials_never_follow_redirect(runtime, location):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(302, headers={"location": location})

    client = runtime.OpenApiClientBase(
        "https://provider.example",
        auth=httpx.BasicAuth("fixture", "not-a-secret"),
        allow_plaintext=True,
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(RuntimeError, match="302"):
        client.execute("items", {"action": "getItem", "path": {"id": "abc"}})
    assert len(seen) == 1
    assert seen[0].url.host == "provider.example"
    assert seen[0].url.scheme == "https"
    client.close()


def test_plaintext_opt_in_preserves_https_verification(runtime, monkeypatch):
    from agent_connector_sdk.http import client as sdk_client

    captured = {}

    def transport(**kwargs):
        captured.update(kwargs)
        return httpx.MockTransport(lambda _: httpx.Response(200, json={"ok": True}))

    monkeypatch.setattr(sdk_client.httpx, "HTTPTransport", transport)
    client = runtime.OpenApiClientBase(
        "https://provider.example",
        auth=httpx.Auth(),
        allow_plaintext=True,
    )
    assert captured["verify"].check_hostname is True
    assert captured["verify"].verify_mode == ssl.CERT_REQUIRED
    client.close()


def test_tampered_contract_cannot_escape_origin(runtime):
    runtime.CONTRACT["operations"]["getItem"]["path"] = "https://other.example/{id}"
    client = runtime.OpenApiClientBase(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(lambda _: pytest.fail("cross-origin request")),
    )
    with pytest.raises(ValueError, match="origin"):
        client.execute("items", {"action": "getItem", "path": {"id": "abc"}})
    client.close()


@pytest.mark.parametrize(
    "media,schema,wire,expected",
    [
        ("text/plain", {"type": "string", "enum": ["ok"]}, b"ok", "ok"),
        ("application/vnd.apple.mpegurl", {"type": "string"}, b"#EXTM3U", "#EXTM3U"),
        (
            "application/octet-stream",
            {"type": "string", "format": "binary"},
            b"\x00\xff",
            "AP8=",
        ),
        (
            "application/problem+json",
            {"type": "object", "required": ["ok"]},
            b'{"ok":true}',
            {"ok": True},
        ),
    ],
)
def test_declared_response_representation(
    runtime, document, media, schema, wire, expected
):
    document["paths"]["/items/{id}"]["get"]["responses"]["200"]["content"] = {
        media: {"schema": schema}
    }
    contract = compile_contract(document)
    domain_schemas = importlib.import_module("openapi_schema").domain_schemas
    contract["schemas"] = {
        domain: domain_schemas(contract, domain) for domain in contract["domains"]
    }
    runtime.CONTRACT = contract
    client = runtime.OpenApiClientBase(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(
            lambda _: httpx.Response(200, content=wire, headers={"content-type": media})
        ),
    )
    assert (
        client.execute("items", {"action": "getItem", "path": {"id": "abc"}})["data"]
        == expected
    )
    client.close()


def test_unknown_response_encoding_fails_compilation(document):
    document["paths"]["/items/{id}"]["get"]["responses"]["200"]["content"] = {
        "application/unknown": {"schema": {"type": "string"}}
    }
    with pytest.raises(ValueError, match="Unsupported response media"):
        compile_contract(document)


def test_scaffold_public_converter_registered_tool_call(
    tmp_path, document, monkeypatch
):
    import asyncio
    import subprocess

    _require_runtime()
    from agent_connector_sdk.http.client import create_http_client
    from fastmcp import Client, FastMCP

    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "scaffold_package.py"),
            "public-fixture",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
    )
    project = tmp_path / "public-fixture"
    spec = tmp_path / "public.json"
    spec.write_text(json.dumps(document))
    generate(spec, project / "public_fixture")
    monkeypatch.syspath_prepend(str(project))
    auth = importlib.import_module("public_fixture.auth")
    runtime = importlib.import_module("public_fixture.openapi_runtime")
    registrar = importlib.import_module("public_fixture.mcp")
    monkeypatch.setattr(auth, "load_config", lambda: None)
    monkeypatch.setattr(
        auth,
        "setting",
        lambda key, default: (
            "https://provider.example" if key.endswith("_BASE_URL") else default
        ),
    )
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(
        runtime,
        "create_http_client",
        lambda options, **kwargs: create_http_client(
            options, transport=httpx.MockTransport(handler)
        ),
    )
    server = FastMCP("Generated public connector fixture")
    registrar.register_items_tools(server)

    async def call():
        async with Client(server) as client:
            result = await client.call_tool(
                "get_item", {"path": {"id": "abc"}}
            )
            assert result.structured_content["data"] == {"ok": True}

    try:
        asyncio.run(call())
        assert len(seen) == 1
        assert seen[0].method == "GET"
        assert not seen[0].headers.get("authorization")
    finally:
        auth.close_client()


def test_converted_client_preserves_generated_auth_contract(tmp_path, document):
    import subprocess

    _require_runtime()
    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "scaffold_package.py"),
            "auth-fixture",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
    )
    project = tmp_path / "auth-fixture"
    document["components"] = {
        "securitySchemes": {"bearer": {"type": "http", "scheme": "bearer"}}
    }
    document["security"] = [{"bearer": []}]
    spec = tmp_path / "auth.json"
    spec.write_text(json.dumps(document))
    generate(spec, project / "auth_fixture", "bearer")
    environment = dict(os.environ, AUTH_FIXTURE_AUTH_SCHEME="bearer")
    # Exercise the unchanged scaffold tests against the replacement OpenAPI factory.
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_auth.py", "-q", "-o", "addopts="],
        cwd=project,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "6 passed" in result.stdout


def test_registrar_keeps_sdk_domain_toggle(runtime, monkeypatch):
    from agent_connector_sdk.mcp import tool_surface
    from fastmcp import FastMCP

    registrar = importlib.import_module("fixture_connector.mcp")
    monkeypatch.setattr(
        tool_surface,
        "setting",
        lambda key, default: False if key == "ITEMSTOOL" else default,
    )
    server = FastMCP("Disabled generated domain")
    assert (
        tool_surface.register_tool_surface(
            server, service="fixture", tools_module=registrar
        )
        == []
    )
    assert tool_surface.registered_tools(server) == {}
    monkeypatch.setattr(tool_surface, "setting", lambda key, default: default)
    assert tool_surface.register_tool_surface(
        server, service="fixture", tools_module=registrar
    ) == ["items"]
    assert set(tool_surface.registered_tools(server)) == {
        parity_name(action) for action in importlib.import_module(
            "fixture_connector.openapi_runtime"
        ).CONTRACT["domains"]["items"]
    }
