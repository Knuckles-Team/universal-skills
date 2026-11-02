"""Declared session credentials never escape their provider origin or enter tools."""

import importlib
import json
import os
import sys
from pathlib import Path

import httpx
import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/skills/mcp-builder/scripts"
)
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "templates"))
generate = importlib.import_module("openapi_converter").generate
schemes = importlib.import_module("openapi_auth_scheme")


@pytest.mark.parametrize("header", ["session", "x-api-key"])
def test_typed_declared_header(header):
    scheme = schemes.declared_scheme(
        "credential",
        {
            "credential": {"type": "apiKey", "in": "header", "name": header},
        },
    )
    assert scheme.kind is schemes.AuthKind.HEADER
    assert scheme.header == header
    assert scheme.name == "credential"


@pytest.mark.parametrize(
    "header",
    [
        "Host",
        "Cookie",
        "Connection",
        "Content-Length",
        "Transfer-Encoding",
        "session\r\ninjected",
        "",
        None,
    ],
)
def test_unsafe_header_declaration_fails(header):
    with pytest.raises(ValueError):
        schemes.declared_scheme(
            "session",
            {
                "session": {"type": "apiKey", "in": "header", "name": header},
            },
        )


def test_bearer_and_public_are_distinct():
    assert schemes.declared_scheme("", {}) is None
    scheme = schemes.declared_scheme(
        "key", {"key": {"type": "http", "scheme": "Bearer"}}
    )
    assert scheme.kind is schemes.AuthKind.BEARER
    assert scheme.header == ""
    with pytest.raises(ValueError, match="not declared"):
        schemes.declared_scheme("unknown", {})


@pytest.fixture
def provider(tmp_path, monkeypatch):
    if os.environ.get("MCP_BUILDER_REQUIRE_SDK") == "1":
        importlib.import_module("scion_sdk.http.client")
        importlib.import_module("regex")
    else:
        pytest.importorskip("scion_sdk.http.client")
        pytest.importorskip("regex")
    from scion_sdk.http.client import create_http_client

    package = tmp_path / "session_fixture"
    package.mkdir()
    (package / "__init__.py").write_text("")
    spec = tmp_path / "fixture.json"
    spec.write_text(
        json.dumps(
            {
                "openapi": "3.0.3",
                "components": {
                    "securitySchemes": {
                        "signed_session": {
                            "type": "apiKey",
                            "in": "header",
                            "name": "session",
                        },
                        "api_key": {"type": "http", "scheme": "bearer"},
                    }
                },
                "security": [{"signed_session": []}],
                "paths": {
                    "/records": {
                        "get": {
                            "operationId": "listRecords",
                            "tags": ["Records"],
                            "parameters": [
                                {
                                    "name": "SeSsIoN",
                                    "in": "header",
                                    "schema": {"type": "string"},
                                }
                            ],
                            "responses": {
                                "200": {
                                    "content": {
                                        "application/json": {
                                            "schema": {"type": "object"}
                                        }
                                    }
                                }
                            },
                        }
                    }
                },
            }
        )
    )
    first = generate(spec, package, "signed_session")
    assert generate(spec, package, "signed_session") == first
    assert "openapi_auth_scheme.py" in first
    for name in list(sys.modules):
        if name == "session_fixture" or name.startswith("session_fixture."):
            del sys.modules[name]
    monkeypatch.syspath_prepend(str(tmp_path))
    auth = importlib.import_module("session_fixture.auth")
    runtime = importlib.import_module("session_fixture.openapi_runtime")
    monkeypatch.setattr(auth, "load_config", lambda: None)
    for key, value in {
        "SESSION_FIXTURE_BASE_URL": "https://provider.example.invalid",
        "SESSION_FIXTURE_TOKEN_REF": "env://SESSION_FIXTURE_VALUE",
        "SESSION_FIXTURE_VALUE": "signed-fixture-session",
    }.items():
        monkeypatch.setenv(key, value)
    for key in ["SESSION_FIXTURE_ALLOW_PLAINTEXT", "SESSION_FIXTURE_AUTH_SCHEME"]:
        monkeypatch.delenv(key, raising=False)
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"records": []})

    def install_handler(callback):
        monkeypatch.setattr(
            runtime,
            "create_http_client",
            lambda options, **kwargs: create_http_client(
                options, transport=httpx.MockTransport(callback)
            ),
        )

    install_handler(handler)
    yield auth, runtime, seen, install_handler
    auth.close_client()


def test_session_factory_uses_reference_and_exact_header(provider):
    auth, _, seen, _ = provider
    client = auth.get_client()
    assert client.credential_scheme == "signed_session"
    assert client.execute("records", {"action": "listRecords"})["data"] == {
        "records": []
    }
    assert seen[0].headers["session"] == "signed-fixture-session"
    assert "authorization" not in seen[0].headers
    assert "signed-fixture-session" not in repr(client.session.auth)


@pytest.mark.parametrize(
    "target",
    [
        "https://other.example.invalid/records",
        "https://provider.example.invalid:8443/records",
        "http://provider.example.invalid/records",
        "//other.example.invalid/records",
    ],
)
def test_session_never_reaches_another_origin(provider, target):
    auth, runtime, seen, _ = provider
    runtime.CONTRACT["operations"]["listRecords"]["path"] = target
    with pytest.raises(ValueError, match="origin"):
        auth.get_client().execute("records", {"action": "listRecords"})
    assert seen == []


def test_session_redirect_is_not_followed(provider):
    auth, _, seen, install = provider

    def redirect(request):
        seen.append(request)
        return httpx.Response(
            302, headers={"location": "https://other.example.invalid"}
        )

    install(redirect)
    with pytest.raises(RuntimeError, match="302"):
        auth.get_client().execute("records", {"action": "listRecords"})
    assert len(seen) == 1
    assert seen[0].url.host == "provider.example.invalid"


@pytest.mark.parametrize(
    "origin",
    ["http://provider.example.invalid", "http://localhost", "http://127.0.0.1"],
)
def test_session_plaintext_requires_explicit_opt_in(provider, monkeypatch, origin):
    auth, _, seen, _ = provider
    monkeypatch.setenv("SESSION_FIXTURE_BASE_URL", origin)
    with pytest.raises(ValueError, match="plaintext"):
        auth.get_client()
    assert seen == []


def test_plaintext_opt_in_is_still_origin_bound(provider, monkeypatch):
    auth, runtime, seen, _ = provider
    monkeypatch.setenv("SESSION_FIXTURE_BASE_URL", "http://provider.example.invalid")
    monkeypatch.setenv("SESSION_FIXTURE_ALLOW_PLAINTEXT", "true")
    client = auth.get_client()
    client.execute("records", {"action": "listRecords"})
    runtime.CONTRACT["operations"]["listRecords"]["path"] = (
        "https://provider.example.invalid/records"
    )
    with pytest.raises(ValueError, match="origin"):
        client.execute("records", {"action": "listRecords"})
    assert len(seen) == 1


@pytest.mark.parametrize("public", [False, True])
def test_session_cannot_be_supplied_by_tool_arguments(provider, monkeypatch, public):
    auth, runtime, seen, _ = provider
    if public:
        monkeypatch.setenv("SESSION_FIXTURE_TOKEN_REF", "")
        runtime.CONTRACT["operations"]["listRecords"]["security"] = []
    with pytest.raises(ValueError, match="controlled by credentials"):
        auth.get_client().execute(
            "records",
            {"action": "listRecords", "header": {"SeSsIoN": "untrusted-literal"}},
        )
    assert seen == []


def test_bearer_cannot_satisfy_session_requirement(provider, monkeypatch):
    auth, _, seen, _ = provider
    monkeypatch.setenv("SESSION_FIXTURE_AUTH_SCHEME", "api_key")
    with pytest.raises(PermissionError):
        auth.get_client().execute("records", {"action": "listRecords"})
    assert seen == []


def test_literal_session_is_rejected(provider, monkeypatch):
    auth, _, seen, _ = provider
    monkeypatch.setenv("SESSION_FIXTURE_TOKEN_REF", "untrusted-literal")
    with pytest.raises(ValueError):
        auth.get_client()
    assert seen == []
