---
name: mcp-client
domain: agent-tools
skill_type: skill
description: >-
  Universal MCP client for connecting to any MCP server directly from a skill.
  This replaces the old multi-agent pattern where the parent agent held all MCP
  tools — instead, each skill spawns its own MCP connection with only the tools it
  needs.
license: MIT
tags: [mcp, client, fastmcp, tools, stdio, http, config]
metadata:
  version: '1.7.0'
  author: Knuckles-Team
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

## Steps

1. List the server's tools with `python -m universal_skills.skills.mcp-client.scripts.mcp_client --url http://github-mcp:8787/mcp --action list-mcp-tools` (or `--command <server>` for stdio).
   Verify that stdout is a JSON listing that includes the tool you plan to call.
2. Write the tool arguments as JSON, inline or in a file with `echo '{"sysparm_limit": "5"}' > args.json`.
   Verify with `python3 -c "import json; json.load(open('args.json'))"` that the file parses.
3. Call the tool with `--action call-mcp-tool --tool-name <tool> --tool-args args.json` and the same connection flags.
   Verify that stdout is a JSON result and that `stderr` shows no error.
4. For repeated use, generate a focused config with `--action generate-mcp-config --mcp-command <server> --enable-tag <TAG> --all-tags "<TAG1,TAG2>" -o mcp_config.json`.
   Verify that `python3 -c "import json; print(json.load(open('mcp_config.json')))"` prints a config naming the server.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| "Operation timed out" | The server is slow to start or the call is heavy | Re-run with `--timeout 120` (or higher) and `--debug` to see where it stalls |
| Connection refused | The MCP server is not running or `--url`/`--command` is wrong | Start the server, confirm the URL or command against the matching file in `references/`, then repeat step 1 |
| Nothing on stdout | The script failed before printing a result | Read `stderr` and re-run with `--debug` to see the import or protocol error; check that `fastmcp` is installed with `pip show fastmcp` |
| Tool returns "not found" | The tool tag is disabled by an environment variable | Pass the enabling variable, for example `--env INCIDENTSTOOL=True`, and list the tools again |

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

The `references/` directory contains ready-to-use documentation for each MCP server. Each `.md` has the stdio (default) command and environment, HTTP connection examples, available tool tags, and single-tag examples. The client config file is yours to write: the skill ships no server config.

| MCP Server | Reference | Tool Tags |
|-----------|-----------|-----------|
| ServiceNow | [servicenow-api.md](references/servicenow-api.md) | 30 |
| Arr Stack | [arr-mcp.md](references/arr-mcp.md) | 7 |
| GitHub | [github-mcp.md](references/github-mcp.md) | 19 |
| GitLab | [gitlab-api.md](references/gitlab-api.md) | 19 |
| Home Assistant | [home-assistant-agent.md](references/home-assistant-agent.md) | 7 |
| Microsoft 365 | [microsoft-agent.md](references/microsoft-agent.md) | 37 |
| Container Manager | [container-manager-mcp.md](references/container-manager-mcp.md) | 10 |
| Nextcloud | [nextcloud-agent.md](references/nextcloud-agent.md) | 6 |
| Plane | [plane-mcp.md](references/plane-mcp.md) | 10 |
| Systems Manager | [systems-manager.md](references/systems-manager.md) | 17 |
| Wger Fitness | [wger-agent.md](references/wger-agent.md) | 7 |
| Mealie | [mealie-mcp.md](references/mealie-mcp.md) | 11 |
| Repository Manager | [repository-manager.md](references/repository-manager.md) | 4 |
| Ansible Tower | [ansible-tower-mcp.md](references/ansible-tower-mcp.md) | 0 |
| Jellyfin | [jellyfin-mcp.md](references/jellyfin-mcp.md) | 62 |
| qBittorrent Manager | [qbittorrent-agent.md](references/qbittorrent-agent.md) | 6 |
| Portainer | [portainer-agent.md](references/portainer-agent.md) | 10 |
| Postiz Agent | [postiz-agent.md](references/postiz-agent.md) | 5 |
| Uptime Kuma | [uptime-kuma-agent.md](references/uptime-kuma-agent.md) | 2 |
| Owncast Agent | [owncast-agent.md](references/owncast-agent.md) | 2 |
| Langfuse Agent | [langfuse-agent.md](references/langfuse-agent.md) | 2 |
| Stirling PDF Agent | [stirlingpdf-agent.md](references/stirlingpdf-agent.md) | 1 |
| LeanIX Agent | [leanix-agent.md](references/leanix-agent.md) | 2 |
| ArchiveBox API | [archivebox-api.md](references/archivebox-api.md) | 3 |
| Audio Transcriber | [audio-transcriber-mcp.md](references/audio-transcriber-mcp.md) | 1 |
| DocumentDB MCP | [documentdb-mcp.md](references/documentdb-mcp.md) | 1 |
| Media Downloader | [media-downloader-mcp.md](references/media-downloader-mcp.md) | 1 |
| SearXNG MCP | [searxng-mcp.md](references/searxng-mcp.md) | 1 |
| Tunnel Manager | [tunnel-manager-mcp.md](references/tunnel-manager-mcp.md) | 1 |
| Vector MCP | [vector-mcp.md](references/vector-mcp.md) | 1 |


## Dependencies

- `fastmcp` (required)
