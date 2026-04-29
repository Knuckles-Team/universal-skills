# Custom FastMCP Server Implementation Guide

## Overview

This document provides the standard architectural pattern, configuration boilerplate, and template required for building custom MCP servers based on the `fastmcp` client and `agent_utilities` libraries.

All new Python MCP servers MUST follow this precise structural pattern.

---

## The Standard Boilerplate

Your `mcp_server.py` must use the custom CLI argument parsing tool `create_mcp_parser()`, the standard context `config`, and include the required `Eunomia`, `RateLimiting`, and `UserToken` middlewares dynamically built in the `mcp_server()` function.

Below is the complete generic template. You must copy and adapt this code, customizing the constants, name, tool signatures, and inner implementations as needed.

```python
#!/usr/bin/python
# coding: utf-8
import os
import sys
import requests
import logging
from typing import Optional, Dict, List, Union, Any

from dotenv import load_dotenv, find_dotenv
from eunomia_mcp.middleware import EunomiaMcpMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from pydantic import Field
from fastmcp import FastMCP, Context
from fastmcp.server.auth.oidc_proxy import OIDCProxy
from fastmcp.server.auth import OAuthProxy, RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier, StaticTokenVerifier
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.utilities.logging import get_logger

# Import standard internal utilities
from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import (
    create_mcp_server,
    config,
)
from agent_utilities.middlewares import (
    UserTokenMiddleware,
    JWTClaimsLoggingMiddleware,
)

__version__ = "1.0.0"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = get_logger("MyServiceMCPServer")

# Fetch environment variables early
API_URL = os.environ.get("SERVICE_API_URL", None)
API_KEY = os.environ.get("SERVICE_API_KEY", None)

def register_misc_tools(mcp: FastMCP):
    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse({"status": "OK"})

def register_action_tools(mcp: FastMCP):
    @mcp.tool(
        annotations={
            "title": "Service Action",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        tags={"action"}, # Add appropriate tool tags
    )
    async def run_action(
        parameter: str = Field(description="Action parameter", default=None),
        ctx: Context = Field(description="MCP context for progress reporting.", default=None),
    ) -> Dict[str, Any]:
        """
        Executes a specific action using the API.
        Returns a Dictionary response with status, message, data, and error.
        """
        logger.debug(f"Executing action with parameter: {parameter}")

        try:
            if not parameter:
                return {
                    "status": 400,
                    "message": "Invalid input: parameter must not be empty",
                    "data": None,
                    "error": "parameter must not be empty",
                }

            if ctx:
                await ctx.report_progress(progress=0, total=100)

            # Perform API interaction here

            if ctx:
                await ctx.report_progress(progress=100, total=100)

            return {
                "status": 200,
                "message": "Action completed successfully",
                "data": {"result": "ok", "parameter": parameter},
                "error": None,
            }

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else None
            error_msg = f"API error: {e.response.json().get('message', str(e)) if e.response else str(e)}"
            logger.error(f"[API Error] {error_msg}")
            return {
                "status": status_code or 500,
                "message": "Failed to perform action",
                "data": None,
                "error": error_msg,
            }
        except Exception as e:
            logger.error(f"[Error] {str(e)}")
            return {
                "status": 500,
                "message": "Failed to perform action",
                "data": None,
                "error": str(e),
            }


def register_prompts(mcp: FastMCP):
    @mcp.prompt
    def action_prompt(topic: str) -> str:
        return f"Executing the action prompt for: {topic}."

# If there are resources to register, add a register_resources(mcp: FastMCP) method here as well.


def get_mcp_instance() -> tuple[Any, Any, Any, Any]:
    """Initialize and return the MCP instance, args, and middlewares."""
    load_dotenv(find_dotenv())

    args, mcp, middlewares = create_mcp_server(
        name="MyService MCP",
        version=__version__,
        instructions="MyService MCP Server - Manage your services with specialized tools.",
    )

    # Register components dynamically based on toggles
    DEFAULT_MISCTOOL = to_boolean(os.getenv("MISCTOOL", "True"))
    if DEFAULT_MISCTOOL:
        register_misc_tools(mcp)

    DEFAULT_ACTIONTOOL = to_boolean(os.getenv("ACTIONTOOL", "True"))
    if DEFAULT_ACTIONTOOL:
        register_action_tools(mcp)

    register_prompts(mcp)

    # Optionally register resources
    # register_resources(mcp)

    for mw in middlewares:
        mcp.add_middleware(mw)

    registered_tags = []
    return mcp, args, middlewares, registered_tags

def mcp_server() -> None:
    mcp, args, middlewares, registered_tags = get_mcp_instance()

    # Standardized logging (stderr)
    print(f"MyService MCP v{__version__}", file=sys.stderr)
    print(f"Starting MyService MCP Server ({args.transport.upper()})", file=sys.stderr)
    print(f"  Auth: {args.auth_type}", file=sys.stderr)
    print(f"  Dynamic Tags Loaded: {len(registered_tags)}", file=sys.stderr)

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger.error("Invalid transport", extra={"transport": args.transport})
        sys.exit(1)

if __name__ == "__main__":
    mcp_server()
```

## Modularity Strategy

Notice that our standard template delegates logic using explicit `register_*` functions:
- `register_misc_tools(mcp: FastMCP)`
- `register_action_tools(mcp: FastMCP)`
- `register_prompts(mcp: FastMCP)`

This tag-based grouping strategy combined with environment variable toggles (e.g., `os.getenv("ACTIONTOOL", "True")`) provides a standardized mechanism for enabling or disabling tools without code changes.

This ensures the `mcp_server()` function remains purely about parsing runtime configuration parameters and bootstrapping the networking/server functionality. Never implement tool logic directly inside `mcp_server()`.

## Type Hints & Pydantic Validation

All standard input fields into `@mcp.tool` signatures must be fully type-hinted and use Pydantic's `Field(...)` validator to include descriptions and default values. You may also utilize dependencies or contexts via `_client = Depends(get_client)` or `ctx: Context`. For standardized interactions like progress reporting and destructive guards, refer to the [🛠 Context Helpers Guide](./ctx_helpers.md).

## Return Strategy

Responses from endpoints typically return an object formatted like:

```python
{
    "status": 200,
    "message": "Human-readable status text",
    "data": {"any": "API JSON Response Data"},
    "error": None
}
```
Or it returns a strongly typed modeled output, like `Response` or `str`. Use your discretion based on how simple the API is.
