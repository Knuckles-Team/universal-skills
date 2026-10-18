"""Generated tools must use the actual SDK's modern confirmation round trip."""

import asyncio

import httpx
import pytest
from test_mcp_builder_openapi import document as document
from test_mcp_builder_openapi import runtime as runtime


@pytest.mark.parametrize("decision", [True, False, "yes", 1, None, "decline", "cancel"])
@pytest.mark.parametrize("surface", ["direct", "search-proxy"])
def test_real_modern_sdk_confirmation_never_dispatches_unconfirmed(
    runtime, decision, surface
):
    from fastmcp import Client, FastMCP
    from fastmcp.client.elicitation import ElicitResult
    from fastmcp.exceptions import ToolError
    from mcp.shared.exceptions import MCPError

    requests, elicitations = [], []
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
    server = FastMCP("Actual SDK confirmation")
    runtime.register_domain(server, "items", lambda: client)
    if surface == "search-proxy":
        runtime.configure_discovery(
            server,
            {
                "version": 1,
                "client": "confirmation-fixture",
                "discovery": "regex-search",
                **{
                    name: 64_000
                    for name in (
                        "max_input_schema_bytes",
                        "max_output_schema_bytes",
                        "max_tool_bytes",
                        "max_listing_bytes",
                        "max_search_result_bytes",
                    )
                },
            },
        )

    async def consent(message, response_type, params, context):
        elicitations.append(message)
        assert params.requested_schema["properties"]["confirmed"]["type"] == "boolean"
        if decision in ("decline", "cancel"):
            return ElicitResult(action=decision)
        return {} if decision is None else {"confirmed": decision}

    async def run():
        async with Client(server, elicitation_handler=consent, timeout=10) as native:
            assert native.protocol_version == "2026-07-28"
            arguments = {"path": {"id": "one"}}
            name = "delete_item"
            if surface == "search-proxy":
                name, arguments = "call_tool", {"name": name, "arguments": arguments}
            call = native.call_tool(name, arguments)
            if decision is True:
                assert (await call).structured_content["data"] == {"ok": True}
            else:
                with pytest.raises(
                    (MCPError, ToolError), match="Write was not confirmed"
                ):
                    await call
            assert len(elicitations) == 1
            assert len(requests) == (1 if decision is True else 0)

    try:
        asyncio.run(run())
    finally:
        client.close()
