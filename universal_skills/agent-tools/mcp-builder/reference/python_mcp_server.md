# Custom FastMCP Server Implementation Guide

## Overview

This document provides the standard architectural pattern, configuration boilerplate, and template required for building custom MCP servers based on `fastmcp` (4.x) and `agent-connector-sdk`. Every connector goes through the SDK; connectors never import `agent_utilities`.

All new Python MCP servers MUST follow this precise structural pattern.

---

## The Standard Boilerplate

Your `mcp_server.py` must use `create_mcp_server()` from `agent_connector_sdk.mcp.server`, which parses the standard command line, refuses unsafe network exposure, configures authentication, adds `/health` and change subscriptions, and returns an `(args, mcp, middlewares)` tuple. The caller adds the middlewares.

Below is the complete generic template. Customize the constants, tool signatures, and inner implementations as needed.

```python
#!/usr/bin/python
import os
import sys
import logging

from dotenv import load_dotenv, find_dotenv
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse

# Import the connector SDK (never agent_utilities)
from agent_connector_sdk.mcp.network import build_network_serving_config
from agent_connector_sdk.mcp.server import create_mcp_server
from agent_connector_sdk.utilities import to_boolean

__version__ = "1.0.0"

logger = logging.getLogger(__name__)

# Fetch environment variables early
API_URL = os.environ.get("SERVICE_API_URL", None)
API_KEY = os.environ.get("SERVICE_API_KEY", None)


def register_misc_tools(mcp):
    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse({"status": "OK"})


def register_action_tools(mcp):
    @mcp.tool(
        annotations={
            "title": "Service Action",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        tags={"action"},
    )
    async def run_action(
        parameter: str = Field(description="Action parameter", default=None),
    ) -> dict:
        """Executes a specific action using the API."""
        try:
            if not parameter:
                return {
                    "status": 400,
                    "message": "Invalid input: parameter must not be empty",
                    "data": None,
                    "error": "parameter must not be empty",
                }
            # Perform API interaction here
            return {
                "status": 200,
                "message": "Action completed successfully",
                "data": {"result": "ok", "parameter": parameter},
                "error": None,
            }
        except Exception as e:
            logger.error(f"[Error] {e}")
            return {"status": 500, "message": "Failed", "data": None, "error": str(e)}


def register_prompts(mcp):
    @mcp.prompt()
    def action_prompt(topic: str) -> str:
        return f"Executing the action prompt for: {topic}."


def get_mcp_instance():
    """Initialize and return the MCP instance and args."""
    load_dotenv(find_dotenv())

    # create_mcp_server returns (args, mcp, middlewares)
    # - args: parsed CLI arguments (transport, host, port, auth, TLS, allowed hosts)
    # - mcp: configured FastMCP instance (auth, /health, change subscriptions)
    # - middlewares: the standard middleware stack — the caller adds it
    args, mcp, middlewares = create_mcp_server(
        "MyService MCP",
        version=__version__,
        instructions="MyService MCP Server - Manage your services.",
    )
    for middleware in middlewares:
        mcp.add_middleware(middleware)

    # Register tools dynamically based on env-var toggles
    DEFAULT_MISCTOOL = to_boolean(os.getenv("MISCTOOL", "True"))
    if DEFAULT_MISCTOOL:
        register_misc_tools(mcp)

    DEFAULT_ACTIONTOOL = to_boolean(os.getenv("ACTIONTOOL", "True"))
    if DEFAULT_ACTIONTOOL:
        register_action_tools(mcp)

    register_prompts(mcp)

    return args, mcp


def mcp_server() -> None:
    """MCP server entry point — registered as console_scripts in pyproject.toml."""
    print(f"MyService MCP v{__version__}", file=sys.stderr)
    args, mcp = get_mcp_instance()

    serving = build_network_serving_config(args)
    if serving is None:
        mcp.run(transport="stdio")
    else:
        mcp.run(
            transport=args.transport,
            host=args.host,
            port=args.port,
            **serving.fastmcp_run_kwargs(),
        )


if __name__ == "__main__":
    mcp_server()
```

---

## Key Architecture Points

### `create_mcp_server()` Return Signature

```python
args, mcp, middlewares = create_mcp_server(name=..., version=..., instructions=...)
```

- **`args`**: Parsed CLI arguments (transport, host, port, authentication, TLS, allowed hosts)
- **`mcp`**: Configured `FastMCP` instance with authentication, `/health`, visibility filtering and change subscriptions
- **`middlewares`**: The standard middleware stack (error handling, per-caller rate limiting) — add each with `mcp.add_middleware()`

### What `create_mcp_server` handles automatically:
- CLI argument parsing (transport, host, port, authentication, TLS, allowed hosts)
- Authentication setup from the auth flags, with secret references resolved by a credential resolver
- Refusal of a non-loopback listener without authentication, a TLS boundary and an exact `--allowed-hosts` list
- The middleware stack (returned for the caller to add)

You should NOT import middleware classes directly unless you need custom middleware beyond the standard stack.

### Transport Options

| Transport | Use Case | Flag |
|-----------|----------|------|
| `stdio` | Local agent integration, MCP clients | `--transport stdio` (default) |
| `streamable-http` | Remote HTTP access, Docker containers | `--transport streamable-http` |

> **Note**: The `http` transport is deprecated. Use `streamable-http` instead.

---

## Modularity Strategy

Tools are organized using `register_*` functions with tag-based grouping:

```python
def register_search_tools(mcp):
    @mcp.tool(tags={"search"})
    async def search_items(...): ...

def register_admin_tools(mcp):
    @mcp.tool(tags={"admin"})
    async def delete_item(...): ...
```

### Environment Variable Toggles

Every tag group MUST have an explicit toggle:

```python
DEFAULT_SEARCHTOOL = to_boolean(os.getenv("SEARCHTOOL", "True"))
if DEFAULT_SEARCHTOOL:
    register_search_tools(mcp)

DEFAULT_ADMINTOOL = to_boolean(os.getenv("ADMINTOOL", "True"))
if DEFAULT_ADMINTOOL:
    register_admin_tools(mcp)
```

This ensures administrators can disable tool groups without code changes.

### Tag Rules
- Tags MUST be strictly lowercase
- No special characters or spaces
- Use hyphens for multi-word tags if needed (e.g., `user-auth`)

---

## Type Hints & Pydantic Validation

All tool inputs must use Pydantic `Field(...)` for descriptions and defaults:

```python
@mcp.tool(tags={"search"})
async def search_items(
    query: str = Field(description="Search query string"),
    max_results: int = Field(default=20, ge=1, le=100, description="Max results"),
) -> dict:
    """Search for items matching the query."""
    ...
```

For dependency injection, use `Depends()` from FastMCP:

```python
from fastmcp import Depends

def get_client():
    return MyAPIClient(api_key=os.getenv("API_KEY"))

@mcp.tool()
async def get_item(item_id: str, _client=Depends(get_client)) -> dict:
    ...
```

---

## Destructive Operations — `ctx.elicit()`

For destructive operations (delete, stop, purge), use `ctx.elicit()` for user confirmation:

```python
from fastmcp import Context

@mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
async def delete_item(
    item_id: str = Field(description="Item ID to delete"),
    ctx: Context = None,
) -> dict:
    """Delete an item permanently."""
    if ctx:
        confirm = await ctx.elicit(
            message=f"Are you sure you want to delete item {item_id}?",
            schema={"type": "boolean"},
        )
        if not confirm.data:
            return {"status": "cancelled", "message": "Operation cancelled by user"}
    # ... proceed with deletion
```

---

## Return Strategy

Standard response format:

```python
{
    "status": 200,
    "message": "Human-readable status text",
    "data": {"any": "API JSON Response Data"},
    "error": None
}
```

Or return strongly typed Pydantic models for structured output.

---

## Quality Checklist

- [ ] All tools use `Field()` for input descriptions
- [ ] All tag groups have env-var toggles
- [ ] Tags are strictly lowercase
- [ ] `create_mcp_server()` is used (not manual server setup)
- [ ] Transport defaults to `stdio`
- [ ] Destructive tools use `ctx.elicit()` guards
- [ ] `--help` flag works: `python -m your_package.mcp_server --help`
- [ ] Test with MCP Inspector: `npx @modelcontextprotocol/inspector`
