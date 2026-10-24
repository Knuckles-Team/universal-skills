"""Budgeted disclosure using FastMCP's existing search transform and call path."""

from __future__ import annotations

import asyncio
import re

if __package__:
    from .openapi_schema_budget import client_budget, require_schema_budget, wire_tool
else:
    from openapi_schema_budget import client_budget, require_schema_budget, wire_tool


def enforce_disclosure(tools, budget, *, kind="listing"):
    """Keep a budget failure explicit on the native JSON-RPC error path."""
    from mcp.shared.exceptions import MCPError
    from mcp.types import INTERNAL_ERROR

    try:
        return require_schema_budget(tools, budget, kind=kind)
    except ValueError as exc:
        raise MCPError(INTERNAL_ERROR, str(exc)) from exc


def configure_discovery(server, budget=None):
    """Retain all tools and policies; bound listing and exact search responses."""
    if budget is None:
        return
    budget = client_budget(budget)
    previous = getattr(server, "_openapi_schema_budget", None)
    if previous is not None:
        if previous != budget:
            raise ValueError("Cannot replace a server's configured client budget")
        return
    from fastmcp.server.transforms import Transform
    from fastmcp.server.transforms.search import RegexSearchTransform

    def serialize(tools):
        values = [wire_tool(tool) for tool in tools]
        enforce_disclosure(values, budget, kind="search_result")
        return values

    class Search(RegexSearchTransform):
        async def transform_tools(self, tools):
            result = await super().transform_tools(tools)
            enforce_disclosure(result, budget)
            return result

    class Eager(Transform):
        async def list_tools(self, tools):
            enforce_disclosure(tools, budget)
            return tools

    transform = (
        Search(max_results=1, search_result_serializer=serialize)
        if budget["discovery"] == "regex-search"
        else Eager()
    )
    server.add_transform(transform)
    server._openapi_schema_budget = budget


async def inspect_discovery(server, names, budget):
    """Use native listing/search to measure and retrieve every expected schema."""
    from fastmcp import Client

    budget = client_budget(budget)
    configure_discovery(server, budget)
    async with Client(server) as client:
        listed = await asyncio.wait_for(client.list_tools(), timeout=45)
        receipt = {"initial": require_schema_budget(listed, budget), "retrievals": {}}
        if budget["discovery"] == "eager":
            return listed, receipt
        tools = []
        for name in sorted(names):
            result = await asyncio.wait_for(
                client.call_tool(
                    "search_tools", {"pattern": "^" + re.escape(name) + r"(?:\s|$)"}
                ),
                timeout=15,
            )
            rows = result.data
            if isinstance(rows, dict):
                rows = rows.get("result")
            if (
                not isinstance(rows, list)
                or len(rows) != 1
                or rows[0].get("name") != name
            ):
                raise ValueError(f"Exact schema retrieval failed: {name}")
            receipt["retrievals"][name] = require_schema_budget(
                rows, budget, kind="search_result"
            )
            tools.extend(rows)
        return tools, receipt
