"""Generated authorization provenance must gate API and native MCP dispatch."""

import asyncio
import copy
from contextlib import closing
import hashlib
import importlib
import json
import sys
from pathlib import Path

import httpx
import pytest
from test_mcp_builder_openapi import _require_runtime
from test_mcp_builder_reviewed_redirect import redirect_case as redirect_case

SCRIPTS = Path(__file__).parents[1] / "universal_skills/skills/mcp-builder/scripts"
sys.path.insert(0, str(SCRIPTS))
converter = importlib.import_module("openapi_converter")
parity = importlib.import_module("openapi_parity")
METHODS = ("get", "head", "options", "post", "put", "patch", "delete", "trace")
SCHEMES = {
    "token": {"type": "http", "scheme": "bearer"},
    "key": {"type": "apiKey", "in": "header", "name": "X-Test-Key"},
}


def _encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def _digest(value):
    raw = (
        value
        if isinstance(value, bytes)
        else json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    )
    return hashlib.sha256(raw).hexdigest()


def _document():
    return {
        "openapi": "3.1.0",
        "components": {"securitySchemes": copy.deepcopy(SCHEMES)},
        "paths": {
            "/items": {
                method: {
                    "operationId": method + "Item",
                    "tags": ["Items"],
                    "responses": {"204": {"description": "Empty response"}},
                }
                for method in METHODS
            }
        },
    }


@pytest.fixture
def generated(tmp_path, monkeypatch):
    _require_runtime()

    def create(document, overlay=None):
        source = tmp_path / "source.json"
        source.write_bytes(_encoded(document))
        package = tmp_path / "authorization_fixture"
        options = {}
        if overlay is not None:
            overlay_path = tmp_path / "overlay.json"
            overlay_path.write_bytes(_encoded(overlay))
            options = {
                "overlay_path": overlay_path,
                "expected_overlay_sha256": _digest(overlay_path.read_bytes()),
                "evidence_root": tmp_path,
            }
        converter.generate(source, package, **options)
        monkeypatch.syspath_prepend(str(tmp_path))
        for name in list(sys.modules):
            if name == package.name or name.startswith(package.name + "."):
                del sys.modules[name]
        return importlib.import_module(package.name + ".openapi_runtime")

    return create


def _client(runtime, requests, mode="read-only", scheme=None):
    class SyntheticAuth(httpx.Auth):
        def auth_flow(self, request):
            if scheme == "token":
                request.headers["Authorization"] = "Bearer synthetic-fixture"
            elif scheme == "key":
                request.headers["X-Test-Key"] = "synthetic-fixture"
            yield request

    def respond(request):
        requests.append(request)
        return httpx.Response(204)

    return runtime.OpenApiClientBase(
        "https://provider.example",
        auth=SyntheticAuth(),
        credential_scheme=scheme,
        write_mode=mode,
        transport=httpx.MockTransport(respond),
    )


def _call(runtime, client, action, surface, effects):
    domain = runtime.CONTRACT["operations"][action]["domain"]
    if surface == "api":
        return client.execute(domain, {"action": action})
    from fastmcp import Client, FastMCP

    factories, confirmations = effects

    def factory():
        factories.append(action)
        return client

    async def consent(message, response_type, params, context):
        confirmations.append(message)
        return {"confirmed": True}

    server = FastMCP("Authorization provenance fixture")
    runtime.register_domain(server, domain, factory)

    async def invoke():
        async with Client(server, elicitation_handler=consent, timeout=10) as native:
            return await native.call_tool(runtime.operation_tool_name(action), {})

    return asyncio.run(invoke())


def _refusals():
    from fastmcp.exceptions import ToolError
    from mcp.shared.exceptions import MCPError

    return PermissionError, ToolError, MCPError


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("mode", ["read-only", "read-write"])
@pytest.mark.parametrize("surface", ["api", "native-mcp"])
def test_unknown_authorization_refuses_before_credentials_or_confirmation(
    generated, monkeypatch, method, mode, surface
):
    runtime = generated(_document())
    requests, credentials, factories, confirmations = [], [], [], []
    with closing(_client(runtime, requests, mode)) as client:
        original = client._require_credentials

        def require(requirements):
            credentials.append(requirements)
            return original(requirements)

        monkeypatch.setattr(client, "_require_credentials", require)
        with pytest.raises(_refusals(), match="[Aa]uthorization"):
            _call(runtime, client, method + "Item", surface, (factories, confirmations))
    assert not requests
    assert not credentials
    assert not factories
    assert not confirmations


@pytest.mark.parametrize("surface", ["api", "native-mcp"])
@pytest.mark.parametrize(
    "case",
    [
        "operation-public",
        "root-public",
        "override-public",
        "empty-alternative",
        "optional-first",
        "optional-last",
    ],
)
def test_declared_anonymous_access_remains_executable(generated, surface, case):
    document = _document()
    operation = document["paths"]["/items"]["get"]
    if case == "root-public":
        document["security"] = []
    else:
        operation["security"] = {
            "operation-public": [],
            "override-public": [],
            "empty-alternative": [{}],
            "optional-first": [{}, {"token": []}],
            "optional-last": [{"token": []}, {}],
        }[case]
    if case == "override-public":
        document["security"] = [{"token": []}]
    runtime = generated(document)
    compiled = runtime.CONTRACT["operations"]["getItem"]
    assert compiled["security_declaration"] == (
        "root" if case == "root-public" else "operation"
    )
    requests, effects = [], ([], [])
    with closing(_client(runtime, requests)) as client:
        _call(runtime, client, "getItem", surface, effects)
    assert len(requests) == 1
    assert requests[0].url.path == "/items"
    assert not effects[1]


@pytest.mark.parametrize("surface", ["api", "native-mcp"])
@pytest.mark.parametrize(
    "requirements,scheme,allowed",
    [
        ([{"token": []}], None, False),
        ([{"token": []}], "key", False),
        ([{"token": []}], "token", True),
        ([{"key": []}], "key", True),
        ([{"key": []}], "token", False),
        ([{"token": []}, {"key": []}], "key", True),
        ([{"token": []}, {"key": []}], None, False),
        ([{"token": [], "key": []}], "token", False),
    ],
)
def test_required_credentials_preserve_alternatives(
    generated, surface, requirements, scheme, allowed
):
    document = _document()
    document["security"] = requirements
    runtime = generated(document)
    assert runtime.CONTRACT["operations"]["getItem"]["security_declaration"] == "root"
    requests = []
    with closing(_client(runtime, requests, scheme=scheme)) as client:
        if allowed:
            _call(runtime, client, "getItem", surface, ([], []))
        else:
            with pytest.raises(_refusals(), match="credential"):
                _call(runtime, client, "getItem", surface, ([], []))
    assert len(requests) == int(allowed)
    if allowed:
        header = "authorization" if scheme == "token" else "x-test-key"
        assert "synthetic-fixture" in requests[0].headers[header]


@pytest.mark.parametrize("surface", ["api", "native-mcp"])
def test_operation_required_auth_overrides_public_root(generated, surface):
    document = _document()
    document["security"] = []
    document["paths"]["/items"]["get"]["security"] = [{"token": []}]
    runtime = generated(document)
    requests = []
    with closing(_client(runtime, requests)) as client:
        with pytest.raises(_refusals(), match="credential"):
            _call(runtime, client, "getItem", surface, ([], []))
    assert not requests


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("surface", ["api", "native-mcp"])
def test_explicit_public_methods_retain_write_confirmation(generated, method, surface):
    document = _document()
    document["security"] = []
    runtime = generated(document)
    requests, effects = [], ([], [])
    with closing(_client(runtime, requests, "read-write")) as client:
        _call(runtime, client, method + "Item", surface, effects)
    assert len(requests) == 1
    assert requests[0].method == method.upper()
    expected_confirmation = surface == "native-mcp" and method not in {
        "get",
        "head",
        "options",
    }
    assert len(effects[1]) == int(expected_confirmation)


@pytest.fixture
def overlay_case(tmp_path):
    document = _document()
    document["servers"] = [{"url": "/api"}]
    source = b"Explicit public decorator for GET /items.\n"
    (tmp_path / "provider.txt").write_bytes(source)
    evidence = {
        "path": "provider.txt",
        "sha256": _digest(source),
        "source_commit": "1" * 40,
    }
    overlay = {
        "version": 1,
        "raw_source_sha256": _digest(_encoded(document)),
        "effective_source_sha256": _digest(_encoded(document)),
        "evidence_files": [evidence],
        "corrections": [],
        "authorization_classifications": [
            {
                "operation_id": "getItem",
                "method": "GET",
                "path": "/items",
                "source_operation_sha256": _digest(document["paths"]["/items"]["get"]),
                "reviewed_guard_classification": "explicit-public-decorator",
                "precondition_category": "synthetic-fixture",
                "preconditions": "Synthetic provider decoration, no real provider admission.",
                "source_evidence": [{**evidence, "line_start": 1, "line_end": 1}],
            }
        ],
    }
    return document, overlay


@pytest.mark.parametrize("surface", ["api", "native-mcp"])
def test_verified_public_overlay_binds_unprefixed_path_and_exact_action(
    generated, overlay_case, surface
):
    document, overlay = overlay_case
    runtime = generated(document, overlay)
    compiled = runtime.CONTRACT["operations"]["getItem"]
    assert compiled["security_declaration"] == "unknown"
    assert compiled["source_path"] == "/items"
    assert compiled["path"] == "/api/items"
    assert compiled["source_operation_sha256"] == _digest(
        document["paths"]["/items"]["get"]
    )
    requests = []
    with closing(_client(runtime, requests, "read-write")) as client:
        _call(runtime, client, "getItem", surface, ([], []))
        with pytest.raises(_refusals(), match="[Aa]uthorization"):
            _call(runtime, client, "postItem", surface, ([], []))
    assert len(requests) == 1
    assert requests[0].url.path == "/api/items"


@pytest.mark.parametrize("surface", ["api", "native-mcp"])
@pytest.mark.parametrize(
    "field,value",
    [
        ("operation_id", "postItem"),
        ("method", "POST"),
        ("path", "/other"),
        ("source_operation_sha256", "0" * 64),
        ("reviewed_guard_classification", "unreviewed-public"),
    ],
)
def test_foreign_or_stale_public_classification_refuses(
    generated, overlay_case, surface, field, value
):
    runtime = generated(*overlay_case)
    runtime.CONTRACT["provider_overlay"]["authorization_classifications"][0][field] = (
        value
    )
    requests, effects = [], ([], [])
    with closing(_client(runtime, requests, "read-write")) as client:
        with pytest.raises(_refusals(), match="[Aa]uthorization"):
            _call(runtime, client, "getItem", surface, effects)
    assert not requests
    assert not any(effects)


@pytest.mark.parametrize("surface", ["api", "native-mcp"])
@pytest.mark.parametrize("declaration", [None, "", "public", {}, [], True])
def test_missing_or_malformed_declaration_fails_closed(generated, surface, declaration):
    document = _document()
    document["security"] = []
    runtime = generated(document)
    operation = runtime.CONTRACT["operations"]["getItem"]
    if declaration is None:
        operation.pop("security_declaration")
    else:
        operation["security_declaration"] = declaration
    requests, effects = [], ([], [])
    with closing(_client(runtime, requests)) as client:
        with pytest.raises(_refusals(), match="[Aa]uthorization"):
            _call(runtime, client, "getItem", surface, effects)
    assert not requests
    assert not any(effects)


@pytest.mark.parametrize(
    "field,value",
    [
        ("security_declaration", "operation"),
        ("source_path", "/other"),
        ("source_operation_sha256", "0" * 64),
    ],
)
def test_parity_rejects_tampered_authorization_metadata(generated, field, value):
    document = _document()
    runtime = generated(document)
    contract = copy.deepcopy(runtime.CONTRACT)
    contract["operations"]["getItem"][field] = value
    raw = _encoded(document)
    with pytest.raises(ValueError, match="contract differs"):
        parity.verify_contract(document, contract, _digest(raw), source_bytes=raw)


def test_plain_sdk_anonymous_http_is_not_a_generated_auth_boundary():
    _require_runtime()
    from scion_sdk.http.client import create_http_client
    from scion_sdk.http.options import HttpClientOptions

    requests = []
    transport = httpx.MockTransport(
        lambda request: requests.append(request) or httpx.Response(204)
    )
    with create_http_client(
        HttpClientOptions(base_url="https://provider.example", auth=httpx.Auth()),
        transport=transport,
    ) as client:
        assert client.get("/ordinary-public-http").status_code == 204
    assert len(requests) == 1


@pytest.fixture
def public_redirect_case(redirect_case):
    raw, overlay, _root = redirect_case
    document = json.loads(raw)
    document.pop("security")
    correction = overlay["response_corrections"][0]
    effective = copy.deepcopy(document)
    responses = importlib.import_module("openapi_provider_responses")
    effective["paths"]["/mobile"]["get"]["responses"] = {
        "307": responses.redirect_response(correction)
    }
    overlay["raw_source_sha256"] = _digest(_encoded(document))
    overlay["effective_source_sha256"] = _digest(_encoded(effective))
    overlay["authorization_classifications"] = [
        {
            **{
                name: correction[name]
                for name in (
                    "operation_id",
                    "method",
                    "path",
                    "source_operation_sha256",
                    "source_evidence",
                )
            },
            "reviewed_guard_classification": "explicit-public-decorator",
            "precondition_category": "synthetic-fixture",
            "preconditions": "Synthetic public redirect declaration.",
        }
    ]
    return document, overlay, effective


@pytest.mark.parametrize("surface", ["api", "native-mcp"])
@pytest.mark.parametrize("binding", ["raw", "effective"])
def test_public_redirect_correction_keeps_raw_authorization_binding(
    generated, public_redirect_case, surface, binding
):
    document, overlay, effective = public_redirect_case
    runtime = generated(document, overlay)
    operation = runtime.CONTRACT["operations"]["mobile"]
    raw_hash = _digest(document["paths"]["/mobile"]["get"])
    effective_hash = _digest(effective["paths"]["/mobile"]["get"])
    assert operation["security_declaration"] == "unknown"
    assert operation["source_operation_sha256"] == raw_hash != effective_hash
    if binding == "effective":
        operation["source_operation_sha256"] = effective_hash
    requests, effects = [], ([], [])
    location = "demo.app:///callback?code=synthetic"

    def respond(request):
        requests.append(request)
        return httpx.Response(307, headers={"location": location}, content=b"ignored")

    with closing(
        runtime.OpenApiClientBase(
            "https://provider.example",
            auth=httpx.Auth(),
            transport=httpx.MockTransport(respond),
        )
    ) as client:
        if binding == "effective":
            with pytest.raises(_refusals(), match="[Aa]uthorization"):
                _call(runtime, client, "mobile", surface, effects)
            assert not requests
            assert not any(effects)
            return
        result = _call(runtime, client, "mobile", surface, effects)
    assert (result if surface == "api" else result.structured_content) == {
        "action": "mobile",
        "status": 307,
        "content_type": "",
        "data": {"location": location},
    }
    assert len(requests) == 1
    assert str(requests[0].url) == "https://provider.example/mobile"
