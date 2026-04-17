# Container Manager MCP Reference

**Project:** `container-manager-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `DOCKER_HOST` | Required for authentication |

## Available Tool Tags (10)

## Available Tool Tags (10)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `COMPOSETOOL` | `True` | compose_down, compose_ps, compose_up |
| `CONTAINERTOOL` | `True` | exec_in_container, list_containers, prune_containers, remove_container, run_container, stop_container |
| `IMAGETOOL` | `True` | list_images, prune_images, pull_image, remove_image |
| `INFOTOOL` | `True` | get_info, get_version |
| `LOGTOOL` | `True` | compose_logs, get_container_logs |
| `MISCTOOL` | `True` | (Internal tools) |
| `NETWORKTOOL` | `True` | create_network, list_networks, prune_networks, remove_network |
| `SWARMTOOL` | `True` | create_service, init_swarm, leave_swarm, list_nodes, list_services, remove_service |
| `SYSTEMTOOL` | `True` | prune_system |
| `VOLUMETOOL` | `True` | create_volume, list_volumes, prune_volumes, remove_volume |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "container-manager-mcp": {
      "command": "container-manager-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "DOCKER_HOST": "${DOCKER_HOST:-unix:///var/run/docker.sock}",
        "LOGTOOL": "${ LOGTOOL:-True }",
        "SYSTEMTOOL": "${ SYSTEMTOOL:-True }",
        "INFOTOOL": "${ INFOTOOL:-True }",
        "IMAGETOOL": "${ IMAGETOOL:-True }",
        "NETWORKTOOL": "${ NETWORKTOOL:-True }",
        "SWARMTOOL": "${ SWARMTOOL:-True }",
        "CONTAINERTOOL": "${ CONTAINERTOOL:-True }",
        "COMPOSETOOL": "${ COMPOSETOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }",
        "VOLUMETOOL": "${ VOLUMETOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
container-manager-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only COMPOSETOOL enabled:

```json
{
  "mcpServers": {
    "container-manager-mcp": {
      "command": "container-manager-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "DOCKER_HOST": "${DOCKER_HOST:-unix:///var/run/docker.sock}",
        "LOGTOOL": "False",
        "SYSTEMTOOL": "False",
        "INFOTOOL": "False",
        "IMAGETOOL": "False",
        "NETWORKTOOL": "False",
        "SWARMTOOL": "False",
        "CONTAINERTOOL": "False",
        "COMPOSETOOL": "True",
        "MISCTOOL": "False",
        "VOLUMETOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py container-manager-mcp help
```
