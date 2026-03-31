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
  version: '0.1.53'
---
# MCP Client Skill

Universal MCP client for connecting to any MCP server directly from a skill. This replaces the old multi-agent pattern where the parent agent held all MCP tools — instead, each skill spawns its own MCP connection with only the tools it needs.

## Usage

The `mcp_client.py` script is a robust, universal client. It separates informative logs (`stderr`) from machine-readable results (`stdout`), making it ideal for agent consumption.

### General Options

| Flag | Description | Default |
|------|-------------|---------|
| `--timeout` | Timeout in seconds for connection and tool calls | 60 |
| `--debug` | Enable verbose debugging logs to `stderr` | False |
| `--quiet` | Suppress non-essential informative messages | False |

### List Available Tools

```bash
# From a local MCP server (stdio)
python -m universal_skills.skills.mcp-client.scripts.mcp_client \
    --command servicenow-mcp \
    --args "--transport stdio" \
    --env INCIDENTSTOOL=True \
    --env CMDBTOOL=False \
    --action list-mcp-tools

# From a remote MCP server (HTTP)
python -m universal_skills.skills.mcp-client.scripts.mcp_client \
    --url http://github-mcp:8787/mcp \
    --action list-mcp-tools

# From an mcp_config.json
python -m universal_skills.skills.mcp-client.scripts.mcp_client \
    --config mcp_config.json \
    --server my-server \
    --action list-mcp-tools
```

### Call a Specific Tool

You can pass arguments as a JSON string or as a path to a JSON file.

#### Option A: JSON String
```bash
python -m universal_skills.skills.mcp-client.scripts.mcp_client \
    --command servicenow-mcp \
    --args "--transport stdio" \
    --env INCIDENTSTOOL=True \
    --dotenv .env \
    --action call-mcp-tool \
    --tool-name get_incidents \
    --tool-args '{"sysparm_limit": "5"}'
```

#### Option B: JSON File
```bash
# Create an arguments file
echo '{"sysparm_limit": "10", "sysparm_query": "active=true"}' > args.json

# Call the tool using the file
python -m universal_skills.skills.mcp-client.scripts.mcp_client \
    --command servicenow-mcp \
    --args "--transport stdio" \
    --dotenv .env \
    --action call-mcp-tool \
    --tool-name get_incidents \
    --tool-args args.json
```

### Advanced: ServiceNow Flow to Mermaid

Generate full relationship diagrams for ServiceNow Flow Designer flows:

```bash
# 1. Prepare your .env with ServiceNow credentials
# 2. Call the workflow_to_mermaid tool
python -m universal_skills.skills.mcp-client.scripts.mcp_client \
    --command servicenow-mcp \
    --dotenv .env \
    --action call-mcp-tool \
    --tool-name workflow_to_mermaid \
    --tool-args '{"flow_identifiers": ["sys_id_1", "sys_id_2"], "save_to_file": true, "output_dir": "."}'
```

The tool will generate a Markdown file containing the Mermaid diagrams, which you can then view in any Mermaid-compatible viewer.

### Generate an mcp_config.json

Generate a config that enables only one tool tag and disables all others:

```bash
python -m universal_skills.skills.mcp-client.scripts.mcp_client \
    --action generate-mcp-config \
    --mcp-command servicenow-mcp \
    --enable-tag INCIDENTSTOOL \
    --all-tags "MISCTOOL,FLOWSTOOL,APPLICATIONTOOL,CMDBTOOL,CICDTOOL,PLUGINSTOOL,INCIDENTSTOOL,TABLE_APITOOL" \
    -o mcp_config.json
```

### List Resources and Prompts

```bash
python -m universal_skills.skills.mcp-client.scripts.mcp_client --config mcp_config.json --action list-mcp-resources
python -m universal_skills.skills.mcp-client.scripts.mcp_client --config mcp_config.json --action list-mcp-prompts
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
| `--action` | `list-mcp-tools`, `call-mcp-tool`, `list-mcp-resources`, `list-mcp-prompts`, `generate-mcp-config` |
| `--tool-name` | Tool name for `call-mcp-tool` |
| `--tool-args` | JSON arguments for `call-mcp-tool` (string OR path to `.json` file) |
| `--mcp-command` | MCP command for `generate-mcp-config` |
| `--enable-tag` | Env var to enable for `generate-mcp-config` |
| `--all-tags` | Comma-separated list of all tool tag env vars |
| `-o, --output` | Output file for `generate-mcp-config` |

## Troubleshooting

- **Timeout Errors**: If you see "Operation timed out", increase the `--timeout` value (e.g., `--timeout 120`).
- **Connection Refused**: Ensure the MCP server is running and the `--url` or `--command` is correct.
- **Dependency Issues**: Run with `--debug` to see detailed import or protocol errors.
- **No Result on stdout**: Check `stderr` for errors. If using `call-tool`, the script should always output a JSON response even on failure.

## References

The `references/` directory contains ready-to-use documentation and `mcp_config.json` files for each MCP server. Each `.md` has stdio (default) + HTTP connection examples, available tool tags, and single-tag config examples.

| MCP Server | Reference | Config | Tool Tags |
|-----------|-----------|--------|-----------|
| ServiceNow | [servicenow-api.md](references/servicenow-api.md) | [servicenow-api.json](references/servicenow-api.json) | 30 |
| AdGuard Home | [adguard-home-agent.md](references/adguard-home-agent.md) | [adguard-home-agent.json](references/adguard-home-agent.json) | 15 |
| Arr Stack | [arr-mcp.md](references/arr-mcp.md) | [arr-mcp.json](references/arr-mcp.json) | 7 |
| GitHub | [github-mcp.md](references/github-mcp.md) | [github-mcp.json](references/github-mcp.json) | 19 |
| GitLab | [gitlab-api.md](references/gitlab-api.md) | [gitlab-api.json](references/gitlab-api.json) | 19 |
| Home Assistant | [home-assistant-agent.md](references/home-assistant-agent.md) | [home-assistant-agent.json](references/home-assistant-agent.json) | 7 |
| Microsoft 365 | [microsoft-agent.md](references/microsoft-agent.md) | [microsoft-agent.json](references/microsoft-agent.json) | 37 |
| Container Manager | [container-manager-mcp.md](references/container-manager-mcp.md) | [container-manager-mcp.json](references/container-manager-mcp.json) | 10 |
| Nextcloud | [nextcloud-agent.md](references/nextcloud-agent.md) | [nextcloud-agent.json](references/nextcloud-agent.json) | 6 |
| Plane | [plane-mcp.md](references/plane-mcp.md) | [plane-mcp.json](references/plane-mcp.json) | 10 |
| Systems Manager | [systems-manager.md](references/systems-manager.md) | [systems-manager.json](references/systems-manager.json) | 17 |
| Wger Fitness | [wger-agent.md](references/wger-agent.md) | [wger-agent.json](references/wger-agent.json) | 7 |
| Mealie | [mealie-mcp.md](references/mealie-mcp.md) | [mealie-mcp.json](references/mealie-mcp.json) | 11 |
| Repository Manager | [repository-manager.md](references/repository-manager.md) | [repository-manager.json](references/repository-manager.json) | 4 |
| Ansible Tower | [ansible-tower-mcp.md](references/ansible-tower-mcp.md) | [ansible-tower-mcp.json](references/ansible-tower-mcp.json) | 0 |
| Jellyfin | [jellyfin-mcp.md](references/jellyfin-mcp.md) | [jellyfin-mcp.json](references/jellyfin-mcp.json) | 62 |
| qBittorrent Manager | [qbittorrent-agent.md](references/qbittorrent-agent.md) | [qbittorrent-agent.json](references/qbittorrent-agent.json) | 6 |
| Portainer | [portainer-agent.md](references/portainer-agent.md) | [portainer-agent.json](references/portainer-agent.json) | 10 |
| Postiz Agent | [postiz-agent.md](references/postiz-agent.md) | [postiz-agent.json](references/postiz-agent.json) | 5 |
| Uptime Kuma | [uptime-kuma-agent.md](references/uptime-kuma-agent.md) | [uptime-kuma-agent.json](references/uptime-kuma-agent.json) | 2 |
| Owncast Agent | [owncast-agent.md](references/owncast-agent.md) | [owncast-agent.json](references/owncast-agent.json) | 2 |
| Langfuse Agent | [langfuse-agent.md](references/langfuse-agent.md) | [langfuse-agent.json](references/langfuse-agent.json) | 2 |
| Stirling PDF Agent | [stirlingpdf-agent.md](references/stirlingpdf-agent.md) | [stirlingpdf-agent.json](references/stirlingpdf-agent.json) | 1 |
| LeanIX Agent | [leanix-agent.md](references/leanix-agent.md) | [leanix-agent.json](references/leanix-agent.json) | 2 |
| ArchiveBox API | [archivebox-api.md](references/archivebox-api.md) | [archivebox-api.json](references/archivebox-api.json) | 3 |
| Audio Transcriber | [audio-transcriber-mcp.md](references/audio-transcriber-mcp.md) | [audio-transcriber-mcp.json](references/audio-transcriber-mcp.json) | 1 |
| DocumentDB MCP | [documentdb-mcp.md](references/documentdb-mcp.md) | [documentdb-mcp.json](references/documentdb-mcp.json) | 1 |
| Media Downloader | [media-downloader-mcp.md](references/media-downloader-mcp.md) | [media-downloader-mcp.json](references/media-downloader-mcp.json) | 1 |
| SearXNG MCP | [searxng-mcp.md](references/searxng-mcp.md) | [searxng-mcp.json](references/searxng-mcp.json) | 1 |
| Tunnel Manager | [tunnel-manager-mcp.md](references/tunnel-manager-mcp.md) | [tunnel-manager-mcp.json](references/tunnel-manager-mcp.json) | 1 |
| Vector MCP | [vector-mcp.md](references/vector-mcp.md) | [vector-mcp.json](references/vector-mcp.json) | 1 |


## Dependencies

- `fastmcp` (required)
