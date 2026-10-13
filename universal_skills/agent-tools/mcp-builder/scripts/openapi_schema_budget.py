"""Explicit client budgets for complete, untruncated MCP schema disclosure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

LIMITS = (
    "max_input_schema_bytes",
    "max_output_schema_bytes",
    "max_tool_bytes",
    "max_listing_bytes",
    "max_search_result_bytes",
)


def encoded(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()


def client_budget(value):
    if isinstance(value, (str, Path)):
        value = json.loads(Path(value).read_text())
    fields = {"version", "client", "discovery", *LIMITS}
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError("An explicit version 1 named client schema budget is required")
    _version(value["version"])
    if not isinstance(value["client"], str) or not value["client"].strip():
        raise ValueError("Schema budget must name its target client")
    if value["discovery"] not in ("eager", "regex-search"):
        raise ValueError("Unsupported schema discovery mode")
    if any(type(value[name]) is not int or value[name] <= 0 for name in LIMITS):
        raise ValueError("Every schema byte budget must be a positive integer")
    return dict(value)


def _version(value):
    if type(value) is not int or value != 1:
        raise ValueError("An explicit version 1 named client schema budget is required")


def wire_tool(tool):
    """Measure the same bounded reference expansion served by native FastMCP."""
    from fastmcp.utilities.json_schema import dereference_refs

    if hasattr(tool, "to_mcp_tool"):
        tool = tool.to_mcp_tool()
    if hasattr(tool, "model_dump"):
        tool = tool.model_dump(mode="json", by_alias=True, exclude_none=True)
    value = json.loads(json.dumps(tool))
    for key in ("inputSchema", "outputSchema"):
        if value.get(key) is not None:
            value[key] = dereference_refs(value[key])
    return value


def schema_sizes(tools, *, kind="listing"):
    values = [wire_tool(tool) for tool in tools]
    names = [tool["name"] for tool in values]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate tool names in schema disclosure")
    rows = {}
    for tool in values:
        rows[tool["name"]] = {
            "input_schema_bytes": len(encoded(tool["inputSchema"]))
            if "inputSchema" in tool
            else 0,
            "output_schema_bytes": len(encoded(tool["outputSchema"]))
            if "outputSchema" in tool
            else 0,
            "tool_bytes": len(encoded(tool)),
            "tool_sha256": hashlib.sha256(encoded(tool)).hexdigest(),
        }
    payload = {"tools": values} if kind == "listing" else values
    return {
        "encoding": "canonical compact UTF-8 JSON",
        "kind": kind,
        "payload_bytes": len(encoded(payload)),
        "tools": rows,
    }


def require_schema_budget(tools, budget, *, kind="listing"):
    budget = client_budget(budget)
    if kind not in ("listing", "search_result"):
        raise ValueError("Unsupported disclosure payload kind")
    sizes = schema_sizes(tools, kind=kind)
    violations = []
    for name, row in sizes["tools"].items():
        for key in ("input_schema_bytes", "output_schema_bytes", "tool_bytes"):
            if row[key] > budget["max_" + key]:
                violations.append(f"{name}.{key}={row[key]}")
    if sizes["payload_bytes"] > budget["max_" + kind + "_bytes"]:
        violations.append(f"{kind}={sizes['payload_bytes']}")
    if violations:
        raise ValueError(f"Schema budget exceeded for {budget['client']}: {violations}")
    return {
        **sizes,
        "client": budget["client"],
        "budget_sha256": hashlib.sha256(encoded(budget)).hexdigest(),
    }
