"""Provider-bound redirects are returned as data, never followed or generalized."""

import asyncio
import copy
import importlib
import json
import sys
from pathlib import Path

import httpx
import pytest
from test_mcp_builder_openapi import _require_runtime

SCRIPTS = Path(__file__).parents[1] / "universal_skills/skills/mcp-builder/scripts"
sys.path.insert(0, str(SCRIPTS))
evidence = importlib.import_module("openapi_provider_evidence")
overlay_module = importlib.import_module("openapi_provider_overlay")
responses_module = importlib.import_module("openapi_provider_responses")


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


@pytest.fixture
def redirect_case(tmp_path):
    provider = b"GET mobile returns temporary redirect with app URI\n"
    (tmp_path / "controller.txt").write_bytes(provider)
    reference = {"path": "controller.txt", "sha256": evidence._hash(provider)}
    operation = {
        "operationId": "mobile",
        "tags": ["Auth"],
        "responses": {"200": {"description": ""}},
    }
    document = {
        "openapi": "3.1.1",
        "security": [],
        "paths": {
            "/mobile": {"get": operation},
            "/ping": {
                "get": {
                    "operationId": "ping",
                    "tags": ["Auth"],
                    "responses": {"200": {}},
                }
            },
        },
    }
    correction = {
        "op": "replace-empty-200-with-307",
        "operation_id": "mobile",
        "method": "GET",
        "path": "/mobile",
        "source_operation_sha256": evidence._hash(operation),
        "before_responses_sha256": evidence._hash(operation["responses"]),
        "location_schema": {
            "type": "string",
            "minLength": 1,
            "maxLength": 256,
            "pattern": r"^demo\.app:///callback\?[^\s]*$",
        },
        "source_evidence": [reference],
    }
    effective = copy.deepcopy(document)
    corrected = {"307": responses_module.redirect_response(correction)}
    effective["paths"]["/mobile"]["get"]["responses"] = corrected
    correction["after_responses_sha256"] = evidence._hash(corrected)
    raw = encoded(document)
    overlay = {
        "version": 2,
        "raw_source_sha256": evidence._hash(raw),
        "effective_source_sha256": evidence._hash(encoded(effective)),
        "evidence_files": [reference],
        "corrections": [],
        "authorization_classifications": [],
        "response_corrections": [correction],
    }
    return raw, overlay, tmp_path


def apply(case):
    raw, overlay, root = case
    data = encoded(overlay)
    return overlay_module.apply_provider_overlay(
        raw, data, expected_overlay_sha256=evidence._hash(data), evidence_root=root
    )


@pytest.fixture
def redirect_runtime(redirect_case, monkeypatch):
    _require_runtime()
    raw, overlay, root = redirect_case
    source, sidecar = root / "source.json", root / "overlay.json"
    source.write_bytes(raw)
    sidecar.write_bytes(encoded(overlay))
    package = root / "redirect_fixture"
    package.mkdir()
    (package / "__init__.py").write_text("")
    generate = importlib.import_module("openapi_converter").generate
    kwargs = {
        "overlay_path": sidecar,
        "expected_overlay_sha256": evidence._hash(sidecar.read_bytes()),
        "evidence_root": root,
    }
    assert generate(source, package, **kwargs) == generate(source, package, **kwargs)
    monkeypatch.syspath_prepend(str(root))
    for name in list(sys.modules):
        if name == "redirect_fixture" or name.startswith("redirect_fixture."):
            del sys.modules[name]
    return importlib.import_module("redirect_fixture.openapi_runtime")


def test_redirect_preserves_raw_source_and_unrelated_responses(redirect_case):
    raw, overlay, _ = redirect_case
    effective, receipt = apply(redirect_case)
    assert json.loads(raw)["paths"]["/mobile"]["get"]["responses"] == {
        "200": {"description": ""}
    }
    assert effective["paths"]["/ping"] == json.loads(raw)["paths"]["/ping"]
    assert effective["paths"]["/mobile"]["get"]["responses"] == {
        "307": responses_module.redirect_response(overlay["response_corrections"][0])
    }
    assert receipt["ready"] is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("operation_id", "ping"),
        ("method", "POST"),
        ("path", "/ping"),
        ("source_operation_sha256", "0" * 64),
        ("before_responses_sha256", "0" * 64),
        ("after_responses_sha256", "0" * 64),
        ("op", "allow-redirects"),
        ("source_evidence", []),
        ("location_schema", {"type": "string"}),
    ],
)
def test_response_correction_rejects_invalid_binding(redirect_case, field, value):
    redirect_case[1]["response_corrections"][0][field] = value
    with pytest.raises(ValueError):
        apply(redirect_case)


def test_response_correction_rejects_stale_evidence(redirect_case):
    (redirect_case[2] / "controller.txt").write_bytes(b"changed source")
    with pytest.raises(ValueError, match="Evidence SHA256"):
        apply(redirect_case)


@pytest.mark.parametrize("mutation", ["duplicate", "v1", "body", "unreviewed"])
def test_response_correction_does_not_broaden_source(redirect_case, mutation):
    raw, overlay, root = redirect_case
    if mutation == "unreviewed":
        effective, _ = apply(redirect_case)
        contract = importlib.import_module("openapi_schema").compile_contract(effective)
        assert "redirect_responses" not in contract["operations"]["mobile"]
        return
    if mutation == "duplicate":
        overlay["response_corrections"] *= 2
    elif mutation == "v1":
        overlay["version"] = 1
    else:
        document = json.loads(raw)
        operation = document["paths"]["/mobile"]["get"]
        operation["responses"]["200"]["content"] = {
            "text/plain": {"schema": {"type": "string"}}
        }
        raw = encoded(document)
        overlay["raw_source_sha256"] = evidence._hash(raw)
        correction = overlay["response_corrections"][0]
        correction["source_operation_sha256"] = evidence._hash(operation)
        correction["before_responses_sha256"] = evidence._hash(operation["responses"])
    with pytest.raises(ValueError):
        apply((raw, overlay, root))


@pytest.mark.parametrize("surface", ["api", "native-mcp"])
def test_reviewed_redirect_returns_location_without_following(
    redirect_runtime, surface
):
    runtime, seen = redirect_runtime, []
    location = "demo.app:///callback?code=synthetic%20code"

    def handler(request):
        seen.append(request)
        return httpx.Response(
            307,
            headers={"location": location, "content-type": "text/html"},
            content=b"<p>Redirecting</p>",
        )

    client = runtime.OpenApiClientBase(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(handler),
    )
    expected = {
        "action": "mobile",
        "status": 307,
        "content_type": "",
        "data": {"location": location},
    }
    try:
        if surface == "api":
            assert client.execute("auth", {"action": "mobile"}) == expected
        else:
            from fastmcp import Client, FastMCP

            server = FastMCP("redirect fixture")
            runtime.register_domain(server, "auth", lambda: client)

            async def run():
                async with Client(server) as native:
                    return await native.call_tool(
                        "mobile", {}
                    )

            assert asyncio.run(run()).structured_content == expected
    finally:
        client.close()
    assert len(seen) == 1
    assert str(seen[0].url) == "https://provider.example/mobile"


@pytest.mark.parametrize(
    "action,status,headers",
    [
        ("ping", 307, [("location", "demo.app:///callback?x")]),
        *[
            ("mobile", status, [("location", "demo.app:///callback?x")])
            for status in (200, 301, 302, 303, 308)
        ],
        ("mobile", 307, []),
        ("mobile", 307, [("location", "demo.app:///callback?x")] * 2),
        ("mobile", 307, [("location", "demo.app:///callback?\r\nx")]),
        ("mobile", 307, [("location", "demo.app:///callback?%xx")]),
        ("mobile", 307, [("location", "https://other.example/")]),
        ("mobile", 307, [("location", "demo.app:///callback?" + "a" * 256)]),
    ],
)
def test_redirect_refusals_make_one_request(redirect_runtime, action, status, headers):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(status, headers=headers)

    client = redirect_runtime.OpenApiClientBase(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(handler),
    )
    try:
        with pytest.raises((RuntimeError, ValueError, httpx.RemoteProtocolError)):
            client.execute("auth", {"action": action})
    finally:
        client.close()
    assert len(seen) == 1


def test_redirect_body_remains_bounded(redirect_runtime, monkeypatch):
    monkeypatch.setattr(redirect_runtime, "MAX_BYTES", 4)
    client = redirect_runtime.OpenApiClientBase(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                307, headers={"location": "demo.app:///callback?"}, content=b"12345"
            )
        ),
    )
    try:
        with pytest.raises(RuntimeError, match="limit exceeded"):
            client.execute("auth", {"action": "mobile"})
    finally:
        client.close()
