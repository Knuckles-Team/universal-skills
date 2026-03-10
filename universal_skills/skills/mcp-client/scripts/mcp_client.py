#!/usr/bin/env python3
"""
Universal MCP Client — connect to any MCP server from a skill.

Supports:
  - Stdio transport (spawn a local MCP server)
  - HTTP / Streamable-HTTP transport (connect to a remote server)
  - Standard mcp_config.json files (multi-server configs)

Usage examples:

  # From a remote URL
  python mcp_client.py --url https://mcp.example.com/mcp --action list-tools

  # From a local MCP command (stdio)
  python mcp_client.py --command servicenow-mcp --args "--transport stdio" \\
      --env INCIDENTSTOOL=True --action list-tools

  # From an mcp_config.json file
  python mcp_client.py --config mcp_config.json --server my-server --action list-tools

  # Call a specific tool
  python mcp_client.py --config mcp_config.json --server my-server \\
      --action call-tool --tool-name get_incidents --tool-args '{"sysparm_limit": "5"}'

  # Generate an mcp_config.json for a specific tool tag
  python mcp_client.py --action generate-config \\
      --mcp-command servicenow-mcp \\
      --enable-tag INCIDENTSTOOL \\
      --all-tags "MISCTOOL,FLOWSTOOL,APPLICATIONTOOL,CMDBTOOL,CICDTOOL,INCIDENTSTOOL"
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Union

# Setup logging to stderr
logger = logging.getLogger("mcp-client")
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)
logger.propagate = False  # Don't let it bubble up to root logger

# ── Optional dependency guardrail ──
try:
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport, StreamableHttpTransport
except ImportError:
    print(
        "Error: The 'fastmcp' package is required but not installed.\n"
        "Install it with: pip install fastmcp",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    from fastmcp.mcp_config import CanonicalMCPConfig
except ImportError:
    CanonicalMCPConfig = None


# ─────────────────────────────────────────────
# Core: create_mcp_client
# ─────────────────────────────────────────────
async def create_mcp_client(
    target: Union[str, dict, Path],
    server_name: Optional[str] = None,
    /,
    headers: Optional[dict] = None,
    command: str = "python",
    args: Optional[list[str]] = None,
    env: Optional[dict] = None,
    cwd: Optional[str] = None,
) -> Client:
    """
    Create a FastMCP Client from:
      - str: file path (local .py → stdio) or URL (http(s) → remote)
      - Path: to mcp_config.json (or similar) file
      - dict: inline config (stdio or http)

    If loading from JSON and multiple servers exist, specify server_name.

    Returns:
        A FastMCP Client instance (use as async context manager).
    """
    transport = None

    if isinstance(target, (str, Path)):
        target_str = str(target)

        # ── URL (http/https) ──
        if target_str.startswith(("http://", "https://")):
            transport = StreamableHttpTransport(url=target_str, headers=headers or {})

        else:
            path = Path(target)

            # ── JSON config file ──
            if path.suffix.lower() in {".json", ".jsonc"} or path.name in {
                "mcp.json",
                "mcp_config.json",
            }:
                if not path.exists():
                    raise FileNotFoundError(f"Config file not found: {path}")

                config_dict = json.loads(path.read_text(encoding="utf-8"))

                if CanonicalMCPConfig is not None:
                    transport = _build_transport_from_canonical(
                        config_dict, server_name, command, args, env, cwd, headers
                    )
                else:
                    transport = _build_transport_from_raw(
                        config_dict, server_name, command, args, env, cwd, headers
                    )

            # ── .py script (stdio) ──
            elif path.suffix == ".py" or (
                not path.suffix and not target_str.startswith(("http://", "https://"))
            ):
                transport = StdioTransport(
                    command=command,
                    args=[target_str] + (args or []),
                    env=env,
                    cwd=cwd,
                )
            else:
                raise ValueError(f"Unsupported file/URL: {target}")

    elif isinstance(target, dict):
        transport = _build_transport_from_dict(target, command, args, env, cwd, headers)
    else:
        raise ValueError("target must be str/Path (file/URL) or dict")

    if transport is None:
        raise RuntimeError("Failed to create transport")

    return Client(transport=transport)


# ─────────────────────────────────────────────
# Transport builders
# ─────────────────────────────────────────────
def _build_transport_from_canonical(
    config_dict, server_name, command, args, env, cwd, headers
):
    """Build transport using fastmcp.mcp_config.CanonicalMCPConfig."""
    mcp_config = CanonicalMCPConfig.from_dict(config_dict)

    if server_name:
        server_cfg = mcp_config.mcpServers.get(server_name)
        if not server_cfg:
            raise ValueError(
                f"Server '{server_name}' not found in config. "
                f"Available: {list(mcp_config.mcpServers)}"
            )
    elif len(mcp_config.mcpServers) == 1:
        server_cfg = next(iter(mcp_config.mcpServers.values()))
    else:
        raise ValueError(
            f"Multiple servers in config; specify --server. "
            f"Found: {list(mcp_config.mcpServers)}"
        )

    if server_cfg.transport in {"stdio", "subprocess"}:
        return StdioTransport(
            command=server_cfg.command or command,
            args=server_cfg.args or args or [],
            env={**(env or {}), **(server_cfg.env or {})},
            cwd=server_cfg.cwd or cwd,
        )
    elif server_cfg.transport in {"http", "httpstream", "streamablehttp"}:
        url = (
            server_cfg.url
            or getattr(server_cfg, "httpstream-url", None)
            or getattr(server_cfg, "http-url", None)
        )
        if not url:
            raise ValueError("No URL found in HTTP server config")
        return StreamableHttpTransport(
            url=url,
            headers={**(headers or {}), **(server_cfg.headers or {})},
        )
    else:
        raise ValueError(f"Unsupported transport in config: {server_cfg.transport}")


def _build_transport_from_raw(
    config_dict, server_name, command, args, env, cwd, headers
):
    """Build transport from raw mcpServers JSON (fallback if CanonicalMCPConfig unavailable)."""
    servers = config_dict.get("mcpServers", {})
    if not servers:
        raise ValueError("No mcpServers found in config")

    if server_name:
        cfg = servers.get(server_name)
        if not cfg:
            raise ValueError(
                f"Server '{server_name}' not found. Available: {list(servers)}"
            )
    elif len(servers) == 1:
        cfg = next(iter(servers.values()))
    else:
        raise ValueError(
            f"Multiple servers in config; specify --server. Found: {list(servers)}"
        )

    # Check for URL (HTTP transport)
    url = cfg.get("url")
    if url:
        return StreamableHttpTransport(
            url=url,
            headers={**(headers or {}), **cfg.get("headers", {})},
        )

    # Stdio transport
    return StdioTransport(
        command=cfg.get("command", command),
        args=cfg.get("args", args or []),
        env={**(env or {}), **cfg.get("env", {})},
        cwd=cfg.get("cwd", cwd),
    )


def _build_transport_from_dict(target, command, args, env, cwd, headers):
    """Build transport from an inline dictionary."""
    url = target.get("url")
    if url:
        return StreamableHttpTransport(
            url=url,
            headers={**(headers or {}), **target.get("headers", {})},
        )
    return StdioTransport(
        command=target.get("command", command),
        args=target.get("args", args or []),
        env={**(env or {}), **target.get("env", {})},
        cwd=target.get("cwd", cwd),
    )


# ─────────────────────────────────────────────
# Config generator
# ─────────────────────────────────────────────
def generate_mcp_config(
    mcp_command: str,
    enable_tag: str,
    all_tags: list[str],
    server_name: Optional[str] = None,
    extra_env: Optional[dict] = None,
    transport_args: Optional[list[str]] = None,
) -> dict:
    """
    Generate an mcp_config.json dict that enables only one tool tag
    and disables all others.

    Args:
        mcp_command: The MCP server command (e.g., "servicenow-mcp")
        enable_tag: The env var to set to True (e.g., "INCIDENTSTOOL")
        all_tags: List of all env var names for this MCP server
        server_name: Server name in the config (defaults to mcp_command)
        extra_env: Additional env vars to include (e.g., API keys, URLs)
        transport_args: Args for the MCP command (defaults to ["--transport", "stdio"])

    Returns:
        A dict suitable for writing as mcp_config.json
    """
    env = {}
    for tag in all_tags:
        env[tag] = "True" if tag == enable_tag else "False"

    if extra_env:
        env.update(extra_env)

    name = server_name or mcp_command.replace("-", "_")
    return {
        "mcpServers": {
            name: {
                "command": mcp_command,
                "args": transport_args or ["--transport", "stdio"],
                "env": env,
            }
        }
    }


# ─────────────────────────────────────────────
# CLI interface
# ─────────────────────────────────────────────
async def run_cli(args):
    """Main CLI logic."""
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if args.action == "generate-mcp-config":
        if not args.mcp_command:
            logger.error("--mcp-command is required for generate-mcp-config")
            sys.exit(1)
        if not args.enable_tag:
            logger.error("--enable-tag is required for generate-mcp-config")
            sys.exit(1)
        if not args.all_tags:
            logger.error("--all-tags is required for generate-mcp-config")
            sys.exit(1)

        tags = [t.strip() for t in args.all_tags.split(",")]
        extra_env = {}
        if args.dotenv:
            try:
                from dotenv import dotenv_values

                env_vars = dotenv_values(args.dotenv)
                if env_vars:
                    extra_env.update(env_vars)
            except ImportError:
                logger.error(
                    "python-dotenv is not installed. Install it with: pip install python-dotenv"
                )
                sys.exit(1)

        if args.env:
            for pair in args.env:
                k, v = pair.split("=", 1)
                extra_env[k] = v

        config = generate_mcp_config(
            mcp_command=args.mcp_command,
            enable_tag=args.enable_tag,
            all_tags=tags,
            server_name=args.server,
            extra_env=extra_env or None,
        )

        output = json.dumps(config, indent=2)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            if not args.quiet:
                print(f"Config written to {args.output}", file=sys.stderr)
        else:
            print(output)
        return

    # ── Build the client ──
    try:
        # Default to os.environ so existing vars are preserved by StdioTransport
        env = dict(os.environ)

        if args.dotenv:
            try:
                from dotenv import dotenv_values

                env_vars = dotenv_values(args.dotenv)
                if env_vars:
                    env.update(env_vars)
            except ImportError:
                logger.error(
                    "python-dotenv is not installed. Install it with: pip install python-dotenv"
                )
                sys.exit(1)

        if args.env:
            for pair in args.env:
                k, v = pair.split("=", 1)
                env[k] = v

        if args.config:
            client_coro = create_mcp_client(
                Path(args.config), args.server, env=env or None
            )
        elif args.url:
            client_coro = create_mcp_client(
                args.url, headers=dict(h.split("=", 1) for h in (args.headers or []))
            )
        elif args.command:
            cmd_args = args.args.split() if args.args else ["--transport", "stdio"]
            client_coro = create_mcp_client(
                {"command": args.command, "args": cmd_args, "env": env}
            )
        else:
            logger.error("Provide --config, --url, or --command to connect.")
            sys.exit(1)

        logger.debug(f"Connecting to MCP server with {args.timeout}s timeout...")
        client = await asyncio.wait_for(client_coro, timeout=args.timeout)

        # ── Execute action ──
        async with client:
            if args.action == "list-mcp-tools":
                tools = await asyncio.wait_for(
                    client.list_tools(), timeout=args.timeout
                )
                if not args.quiet:
                    logger.info(f"Found {len(tools)} tools:")
                for t in tools:
                    desc = (t.description or "")[:80]
                    print(f"  • {t.name}: {desc}", file=sys.stderr)
                # Output machine-readable tools to stdout
                print(
                    json.dumps(
                        [{"name": t.name, "description": t.description} for t in tools]
                    )
                )

            elif args.action == "call-mcp-tool":
                if not args.tool_name:
                    logger.error("--tool-name is required for call-mcp-tool")
                    sys.exit(1)

                tool_args = {}
                if args.tool_args:
                    # Check if it's a file path
                    if os.path.isfile(args.tool_args):
                        try:
                            with open(args.tool_args, "r", encoding="utf-8") as f:
                                tool_args = json.load(f)
                        except Exception as e:
                            logger.error(
                                f"Error reading JSON from file {args.tool_args}: {e}"
                            )
                            sys.exit(1)
                    else:
                        # Otherwise parse as raw JSON string
                        try:
                            tool_args = json.loads(args.tool_args)
                        except Exception as e:
                            logger.error(f"Error parsing JSON string: {e}")
                            sys.exit(1)

                logger.debug(f"Calling tool '{args.tool_name}' with args: {tool_args}")
                result = await asyncio.wait_for(
                    client.call_tool(args.tool_name, tool_args), timeout=args.timeout
                )
                print(json.dumps(result, indent=2, default=str))

            elif args.action == "list-mcp-resources":
                resources = await asyncio.wait_for(
                    client.list_resources(), timeout=args.timeout
                )
                if not args.quiet:
                    logger.info(f"Found {len(resources)} resources:")
                for r in resources:
                    print(f"  • {r.uri}: {r.name}", file=sys.stderr)
                print(json.dumps([{"uri": r.uri, "name": r.name} for r in resources]))

            elif args.action == "list-mcp-prompts":
                prompts = await asyncio.wait_for(
                    client.list_prompts(), timeout=args.timeout
                )
                if not args.quiet:
                    logger.info(f"Found {len(prompts)} prompts:")
                for p in prompts:
                    print(f"  • {p.name}: {p.description or ''}", file=sys.stderr)
                print(
                    json.dumps(
                        [
                            {"name": p.name, "description": p.description}
                            for p in prompts
                        ]
                    )
                )

    except asyncio.TimeoutError:
        logger.error(f"Operation timed out after {args.timeout} seconds")
        if args.action == "call-mcp-tool":
            print(
                json.dumps(
                    {"status": "error", "message": f"Timeout after {args.timeout}s"}
                )
            )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.debug)
        if args.action == "call-mcp-tool":
            print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Universal MCP Client — connect to any MCP server.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Connection options (mutually exclusive-ish)
    conn = parser.add_argument_group("Connection")
    conn.add_argument("--config", help="Path to mcp_config.json file")
    conn.add_argument("--url", help="Remote MCP server URL (HTTP/HTTPS)")
    conn.add_argument("--command", help="Local MCP server command (stdio transport)")
    conn.add_argument(
        "--server",
        help="Server name within config (required if config has multiple servers)",
    )
    conn.add_argument(
        "--args",
        help='Arguments for the MCP command (space-separated string, e.g., "--transport stdio")',
    )
    conn.add_argument(
        "--env",
        action="append",
        help="Environment variable for the MCP server (KEY=VALUE, can repeat)",
    )
    conn.add_argument(
        "--headers",
        action="append",
        help="HTTP headers for remote connections (KEY=VALUE, can repeat)",
    )

    # Action
    parser.add_argument(
        "--action",
        required=True,
        choices=[
            "list-mcp-tools",
            "call-mcp-tool",
            "list-mcp-resources",
            "list-mcp-prompts",
            "generate-mcp-config",
        ],
        help="Action to perform",
    )

    # Tool call options
    tool_group = parser.add_argument_group("Tool Call")
    tool_group.add_argument("--tool-name", help="Tool name for call-tool action")
    tool_group.add_argument(
        "--tool-args", help="JSON string of tool arguments for call-tool action"
    )

    # Config generation options
    gen_group = parser.add_argument_group("Config Generation")
    gen_group.add_argument(
        "--mcp-command", help="MCP server command for generate-mcp-config"
    )
    gen_group.add_argument(
        "--enable-tag", help="Tool tag env var to enable (e.g., INCIDENTSTOOL)"
    )
    gen_group.add_argument(
        "--all-tags",
        help="Comma-separated list of all tool tag env vars for this MCP server",
    )
    gen_group.add_argument(
        "--output", "-o", help="Output file path for generate-mcp-config"
    )

    # General options
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds for connection and tool calls",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging to stderr"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress non-result output to stdout"
    )

    # Dotenv support
    env_group = parser.add_argument_group("Environment")
    env_group.add_argument(
        "--dotenv", help="Path to a .env file to load environment variables from"
    )

    parsed_args = parser.parse_args()
    asyncio.run(run_cli(parsed_args))


if __name__ == "__main__":
    main()
