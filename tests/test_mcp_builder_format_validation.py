"""Required format assertions never degrade to successful annotation-only checks."""

import asyncio
import importlib

import httpx
import pytest
import tomllib
from test_mcp_builder_reviewed_redirect import redirect_case as redirect_case
from test_mcp_builder_reviewed_redirect import redirect_runtime as redirect_runtime


def _call(runtime, client, surface):
    if surface == "api":
        return client.execute("auth", {"action": "mobile"})
    from fastmcp import Client, FastMCP

    server = FastMCP("Required URI format fixture")
    runtime.register_domain(server, "auth", lambda: client)

    async def run():
        async with Client(server) as native:
            return await native.call_tool("mobile", {})

    return asyncio.run(run())


@pytest.mark.parametrize("surface", ["api", "native-mcp"])
@pytest.mark.parametrize(
    "problem", ["query-bracket", "two-fragments", "missing-checker"]
)
def test_required_uri_format_refuses_without_following(
    redirect_runtime, monkeypatch, surface, problem
):
    from fastmcp.exceptions import ToolError

    runtime, seen = redirect_runtime, []
    location = {
        "query-bracket": "demo.app:///callback?x=[",
        "two-fragments": "demo.app:///callback?x#one#two",
        "missing-checker": "demo.app:///callback?valid=1",
    }[problem]
    if problem == "missing-checker":
        monkeypatch.delitem(runtime.FormatChecker.checkers, "uri")

    def handler(request):
        seen.append(request)
        return httpx.Response(307, headers={"location": location})

    client = runtime.OpenApiClientBase(
        "https://provider.example",
        auth=httpx.Auth(),
        transport=httpx.MockTransport(handler),
    )
    try:
        with pytest.raises((ValueError, RuntimeError, ToolError)):
            _call(runtime, client, surface)
    finally:
        client.close()
    assert len(seen) == 1
    assert str(seen[0].url) == "https://provider.example/mobile"


@pytest.mark.parametrize("value", ["not-a-date-time", "2026-10-13T14:00:00"])
def test_datetime_rejects_invalid_or_timezone_less_values(redirect_runtime, value):
    with pytest.raises(ValueError, match="declared OpenAPI schema"):
        redirect_runtime.validate(value, {"type": "string", "format": "date-time"})


def test_datetime_accepts_declared_rfc3339_value(redirect_runtime):
    redirect_runtime.validate(
        "2026-10-13T14:00:00Z", {"type": "string", "format": "date-time"}
    )


@pytest.mark.parametrize("name", ["uri", "date-time", "provider-unknown-format"])
def test_unavailable_format_fails_closed(redirect_runtime, monkeypatch, name):
    monkeypatch.delitem(redirect_runtime.FormatChecker.checkers, name, raising=False)
    with pytest.raises(RuntimeError, match="format checker is unavailable"):
        redirect_runtime.validate("value", {"type": "string", "format": name})


def test_generated_packages_declare_required_validator_dependencies():
    converter = importlib.import_module("openapi_converter")
    initial = '[project]\nname = "fixture"\ndependencies = []\n'
    rendered = converter._add_dependencies(initial, [])
    dependencies = tomllib.loads(rendered)["project"]["dependencies"]
    assert "rfc3986-validator>=0.1.1,<0.2" in dependencies
    assert "rfc3339-validator>=0.1.4,<0.2" in dependencies
    assert converter._add_dependencies(rendered, dependencies) == rendered


@pytest.mark.parametrize("suffix", ["\n", "\r", "\t", "\x00"])
def test_redirect_parser_rejects_trailing_controls(redirect_runtime, suffix):
    response_module = importlib.import_module(
        redirect_runtime.__package__ + ".openapi_response"
    )
    response = httpx.Response(
        307, headers={"location": "demo.app:///callback?x=1" + suffix}
    )
    with pytest.raises(ValueError, match="absolute URI"):
        response_module.decode_body(
            redirect_runtime.CONTRACT["operations"]["mobile"], response, b""
        )
