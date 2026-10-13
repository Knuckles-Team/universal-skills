"""Exhaustive serial fixture runner for real API and native MCP dispatch tests.

The connector owns fixtures, its client factory and native MCP call adapter.
Neither validation nor authorization is patched by this runner. Only HTTP is
replaced with MockTransport. The MCP adapter must bind the supplied client to
the actual registered tool and preserve the protocol's confirmation behavior.
"""

from __future__ import annotations

import copy
import hashlib
import json
from contextlib import closing
from urllib.parse import parse_qsl

if __package__:
    from .openapi_parity import require_complete_coverage, verify_contract
    from .openapi_source_parity import verify_source_request
else:
    from openapi_parity import require_complete_coverage, verify_contract
    from openapi_source_parity import verify_source_request


def _check_request(request, expected, operation):
    if request.method != operation["method"] or request.url.path != expected["path"]:
        raise ValueError("Dispatched method or route differs from fixture")
    if list(request.url.params.multi_items()) != [
        tuple(pair) for pair in expected.get("query", [])
    ]:
        raise ValueError("Dispatched query parameters differ from fixture")
    for name, value in expected.get("headers", {}).items():
        if request.headers.get(name) != value:
            raise ValueError("Dispatched header differs from fixture")
    _check_body(request, expected)


def _check_body(request, expected):
    if "json" in expected and json.loads(request.content) != expected["json"]:
        raise ValueError("Dispatched JSON body differs from fixture")
    if "body" in expected and request.content != expected["body"].encode():
        raise ValueError("Dispatched body differs from fixture")

    if "form" in expected and parse_qsl(
        request.content.decode(), keep_blank_values=True
    ) != [tuple(pair) for pair in expected["form"]]:
        raise ValueError("Dispatched form body differs from fixture")


def _transport(fixture, operation, seen, *, assert_request, source_operation):
    try:
        import httpx
    except ImportError as exc:
        raise RuntimeError(
            "Transport parity requires the connector's existing HTTP environment"
        ) from exc

    def respond(request):
        verify_source_request(request, source_operation, fixture["arguments"])
        _check_request(request, fixture["expected_request"], operation)
        if assert_request is not None:
            assert_request(request, operation, fixture)
        seen.append(request)
        return httpx.Response(**copy.deepcopy(fixture["response"]))

    return httpx.MockTransport(respond)


async def verify_transport(
    source: bytes,
    contract,
    fixtures,
    *,
    api_factory,
    mcp_call,
    assert_request=None,
    overlay_bytes=None,
    expected_overlay_sha256=None,
    evidence_root=None,
):
    """Require one successful actual request per operation through both surfaces.

    api_factory(transport, operation) returns a closeable real connector client.
    await mcp_call(tool_name, arguments, client) must call the native MCP tool with
    that client bound as its provider. It must raise on an MCP error. Fixtures map
    every action to arguments, httpx.Response kwargs, expected_request fields and
    expected_result. Multipart fixtures require assert_request to inspect parsed
    fields and files; the runner never skips a declared body representation.
    """
    inventory = verify_contract(
        json.loads(source),
        contract,
        hashlib.sha256(source).hexdigest(),
        source_bytes=source,
        overlay_bytes=overlay_bytes,
        expected_overlay_sha256=expected_overlay_sha256,
        evidence_root=evidence_root,
    )
    require_complete_coverage(contract, fixtures, fixtures)
    covered = {"api": [], "mcp": []}
    adapters = {
        "factory": api_factory,
        "mcp": mcp_call,
        "request": assert_request,
        "source": inventory["operations"],
    }
    for action, operation in sorted(contract["operations"].items()):
        fixture = fixtures[action]
        if fixture["arguments"].get("action") != action:
            raise ValueError("Fixture action does not match its inventory entry")
        _require_body_proof(operation, fixture, assert_request)
        for surface in ("api", "mcp"):
            await _probe_surface(surface, operation, fixture, adapters=adapters)
            covered[surface].append(action)
    result = require_complete_coverage(contract, covered["api"], covered["mcp"])
    return {
        **result,
        "mocked_transport_verified": True,
        "live_endpoint_verified": False,
    }


def _require_body_proof(operation, fixture, assert_request):
    if "body" not in fixture["arguments"]:
        return
    media = operation["content_type"]
    if media == "multipart/form-data":
        if assert_request is None:
            raise ValueError(
                "Multipart transport proof requires a parsed-field assertion"
            )
    elif {"application/json": "json", "application/x-www-form-urlencoded": "form"}[
        media
    ] not in fixture["expected_request"]:
        raise ValueError("Transport fixture must assert the serialized request body")


async def _probe_surface(surface, operation, fixture, *, adapters):
    seen = []
    client = adapters["factory"](
        _transport(
            fixture,
            operation,
            seen,
            assert_request=adapters["request"],
            source_operation=adapters["source"][operation["action"]],
        ),
        operation,
    )
    with closing(client):
        arguments = copy.deepcopy(fixture["arguments"])
        result = await _dispatch(
            surface, operation, arguments, client=client, mcp_call=adapters["mcp"]
        )
        if result != fixture["expected_result"]:
            raise ValueError(f"{surface} response differs from fixture")
        if len(seen) != 1:
            raise ValueError(
                f"{surface} dispatch must reach exactly one mock HTTP request"
            )


async def _dispatch(surface, operation, arguments, *, client, mcp_call):
    if surface == "api":
        return client.execute(operation["domain"], arguments)
    result = await mcp_call(f"{operation['domain']}_operations", arguments, client)
    if getattr(result, "is_error", False) or getattr(result, "isError", False):
        raise ValueError("Native MCP dispatch returned an error")
    return result.structured_content
