---
name: mcp-client
description:
  Connect to any MCP server from within a skill. Supports stdio (local), HTTP (remote),
  and mcp_config.json-based connections. Use to list tools, call tools, list resources,
  and generate per-skill mcp_config.json files with selective tool tags.
license: MIT
tags: [mcp, client, fastmcp, tools, stdio, http, config]
metadata:
  author: Audel Rouhi
  version: '0.1.0'
---
# MCP Client Skill

Universal MCP client for connecting to any MCP server directly from a skill. This replaces the old multi-agent pattern where the parent agent held all MCP tools — instead, each skill spawns its own MCP connection with only the tools it needs.

## Why This Exists

Previously, agents used `mcp_url` and `mcp_config` parameters to connect to MCP servers at the agent level, exposing ALL tools to the LLM context window. This overwhelmed context. Now each skill connects independently, enabling only the specific tool tag it needs.

## Usage

### List Available Tools

```bash
# From a local MCP server (stdio)
python scripts/mcp_client.py \
    --command servicenow-mcp \
    --args "--transport stdio" \
    --env INCIDENTSTOOL=True \
    --env CMDBTOOL=False \
    --action list-tools

# From a remote MCP server (HTTP)
python scripts/mcp_client.py \
    --url http://github-mcp:8787/mcp \
    --action list-tools

# From an mcp_config.json
python scripts/mcp_client.py \
    --config mcp_config.json \
    --server my-server \
    --action list-tools
```

### Call a Specific Tool

```bash
python scripts/mcp_client.py \
    --command servicenow-mcp \
    --args "--transport stdio" \
    --env INCIDENTSTOOL=True \
    --action call-tool \
    --tool-name get_incidents \
    --tool-args '{"sysparm_limit": "5"}'
```

### Generate an mcp_config.json

Generate a config that enables only one tool tag and disables all others:

```bash
python scripts/mcp_client.py \
    --action generate-config \
    --mcp-command servicenow-mcp \
    --enable-tag INCIDENTSTOOL \
    --all-tags "MISCTOOL,FLOWSTOOL,APPLICATIONTOOL,CMDBTOOL,CICDTOOL,PLUGINSTOOL,INCIDENTSTOOL,TABLE_APITOOL" \
    -o mcp_config.json
```

### List Resources and Prompts

```bash
python scripts/mcp_client.py --config mcp_config.json --action list-resources
python scripts/mcp_client.py --config mcp_config.json --action list-prompts
```

## Programmatic Usage

The script exposes two key functions for import:

```python
from universal_skills.skills.mcp_client.scripts.mcp_client import (
    create_mcp_client,
    generate_mcp_config,
)

# Generate a focused config
config = generate_mcp_config(
    mcp_command="servicenow-mcp",
    enable_tag="INCIDENTSTOOL",
    all_tags=["MISCTOOL", "INCIDENTSTOOL", "CMDBTOOL"],
)

# Create and use the client
import asyncio, json, tempfile
from pathlib import Path

async def main():
    cfg_path = Path(tempfile.mktemp(suffix=".json"))
    cfg_path.write_text(json.dumps(config))
    client = await create_mcp_client(cfg_path)
    async with client:
        tools = await client.list_tools()
        result = await client.call_tool("get_incidents", {"sysparm_limit": "5"})
        print(result)

asyncio.run(main())
```

## Arguments Reference

| Argument | Description |
|----------|-------------|
| `--config` | Path to `mcp_config.json` file |
| `--url` | Remote MCP server URL (HTTP/HTTPS) |
| `--command` | Local MCP server command (stdio) |
| `--server` | Server name if config has multiple servers |
| `--args` | Space-separated args for the MCP command |
| `--env` | Environment variable `KEY=VALUE` (repeatable) |
| `--headers` | HTTP header `KEY=VALUE` for remote (repeatable) |
| `--action` | `list-tools`, `call-tool`, `list-resources`, `list-prompts`, `generate-config` |
| `--tool-name` | Tool name for `call-tool` |
| `--tool-args` | JSON arguments for `call-tool` |
| `--mcp-command` | MCP command for `generate-config` |
| `--enable-tag` | Env var to enable for `generate-config` |
| `--all-tags` | Comma-separated list of all tool tag env vars |
| `-o, --output` | Output file for `generate-config` |

## References

The `references/` directory contains ready-to-use documentation and `mcp_config.json` files for each MCP server. Each `.md` has stdio (default) + HTTP connection examples, available tool tags, and single-tag config examples.

| MCP Server | Reference | Config | Tool Tags |
|-----------|-----------|--------|-----------|
| ServiceNow | [servicenow-api.md](references/servicenow-api.md) | [servicenow-api.json](references/servicenow-api.json) | 30 |
| AdGuard Home | [adguard-home-agent.md](references/adguard-home-agent.md) | [adguard-home-agent.json](references/adguard-home-agent.json) | 15 |
| Arr Stack | [arr-mcp.md](references/arr-mcp.md) | [arr-mcp.json](references/arr-mcp.json) | 7 |
| GitLab | [gitlab-api.md](references/gitlab-api.md) | [gitlab-api.json](references/gitlab-api.json) | 19 |
| Microsoft 365 | [microsoft-agent.md](references/microsoft-agent.md) | [microsoft-agent.json](references/microsoft-agent.json) | 37 |
| Container Manager | [container-manager-mcp.md](references/container-manager-mcp.md) | [container-manager-mcp.json](references/container-manager-mcp.json) | 10 |
| Nextcloud | [nextcloud-agent.md](references/nextcloud-agent.md) | [nextcloud-agent.json](references/nextcloud-agent.json) | 6 |
| Systems Manager | [systems-manager.md](references/systems-manager.md) | [systems-manager.json](references/systems-manager.json) | 17 |
| Mealie | [mealie-mcp.md](references/mealie-mcp.md) | [mealie-mcp.json](references/mealie-mcp.json) | 11 |
| Repository Manager | [repository-manager.md](references/repository-manager.md) | [repository-manager.json](references/repository-manager.json) | 4 |
| Ansible Tower | [ansible-tower-mcp.md](references/ansible-tower-mcp.md) | [ansible-tower-mcp.json](references/ansible-tower-mcp.json) | 0 |
| Jellyfin | [jellyfin-mcp.md](references/jellyfin-mcp.md) | [jellyfin-mcp.json](references/jellyfin-mcp.json) | 62 |

## Dependencies

- `fastmcp` (required)
