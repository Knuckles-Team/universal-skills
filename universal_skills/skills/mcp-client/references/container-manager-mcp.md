# Container Manager MCP Reference

**Project:** `container-manager-mcp`
**Entrypoint:** `container-manager-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `DOCKER_HOST` | Required for authentication |

## Available Tool Tags (10)

| Env Variable | Default |
|-------------|----------|
| `COMPOSETOOL` | `True` |
| `CONTAINERTOOL` | `True` |
| `IMAGETOOL` | `True` |
| `INFOTOOL` | `True` |
| `LOGTOOL` | `True` |
| `MISCTOOL` | `True` |
| `NETWORKTOOL` | `True` |
| `SWARMTOOL` | `True` |
| `SYSTEMTOOL` | `True` |
| `VOLUMETOOL` | `True` |

## Stdio Connection (Default)

Spawns the MCP server locally as a subprocess:

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
        "COMPOSETOOL": "True",
        "CONTAINERTOOL": "True",
        "IMAGETOOL": "True",
        "INFOTOOL": "True",
        "LOGTOOL": "True",
        "MISCTOOL": "True",
        "NETWORKTOOL": "True",
        "SWARMTOOL": "True",
        "SYSTEMTOOL": "True",
        "VOLUMETOOL": "True"
      }
    }
  }
}
```

## HTTP Connection

Connects to a running MCP server over HTTP:

```json
{
  "mcpServers": {
    "container-manager-mcp": {
      "url": "http://container-manager-mcp:8787/mcp",
      "timeout": 200000
    }
  }
}
```

## Single-Tag Config Example

Enable only `COMPOSETOOL` and disable all others:

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
        "COMPOSETOOL": "True",
        "CONTAINERTOOL": "False",
        "IMAGETOOL": "False",
        "INFOTOOL": "False",
        "LOGTOOL": "False",
        "MISCTOOL": "False",
        "NETWORKTOOL": "False",
        "SWARMTOOL": "False",
        "SYSTEMTOOL": "False",
        "VOLUMETOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List tools (all tags enabled)
python scripts/mcp_client.py --config references/container-manager-mcp.json --action list-tools

# Generate a single-tag config
python scripts/mcp_client.py --action generate-config \
    --mcp-command container-manager-mcp \
    --enable-tag COMPOSETOOL \
    --all-tags "COMPOSETOOL,CONTAINERTOOL,IMAGETOOL,INFOTOOL,LOGTOOL,MISCTOOL,NETWORKTOOL,SWARMTOOL,SYSTEMTOOL,VOLUMETOOL"
```

## Tailored Skills Reference

### container-manager-mcp-compose

**Description:** Manages Docker Compose. Use for up/down/ps/logs. Triggers - multi-container apps.

#### Overview
Compose for app stacks.

#### Key Tools
- `compose_up`: Start stack. Params: compose_file (required), detach=true, build?.
- `compose_down`: Stop/remove.
- `compose_ps`: List services.
- `compose_logs`: Get logs. Params: service?.

#### Usage Instructions
1. Provide compose_file path.
2. Subset: Service-specific logs.

#### Examples
- Up: `compose_up` with compose_file="docker-compose.yml", build=true.
- Logs: `compose_logs` with service="db".

#### Error Handling
- Invalid YAML: Validate file.
- Conflicts: Down first.

### container-manager-mcp-container

**Description:** Manages containers. Use for listing/running/stopping/removing/pruning. Triggers - runtime ops, scaling.

#### Overview
Core container control. Supports troubleshooting subsets (list -> logs -> exec).

#### Key Tools
- `list_containers`: List running/all. Params: all?, manager_type?.
- `run_container`: Run new. Params: image (required), name?, command?, detach?, ports?, volumes?, environment?.
- `stop_container`: Stop. Params: container_id (required), timeout=10.
- `remove_container`: Remove. Params: container_id (required), force?.
- `prune_containers`: Clean stopped.
- `exec_in_container`: Exec command. Params: container_id (required), command (list), detach?.

#### Usage Instructions
1. Use ID/name for actions.
2. For troubleshooting: list -> get_logs (logs skill) -> exec.

#### Examples
- Run: `run_container` with image="nginx", ports={"80/tcp": "8080"}.
- Exec: `exec_in_container` with container_id="mycont", command=["ls", "-l"].

#### Error Handling
- Not running: Check status first.
- Conflicts: Force for removal.
  Reference `troubleshoot.md` for workflows.

### container-manager-mcp-image

**Description:** Manages container images. Use for listing/pulling/removing/pruning images. Triggers - image ops, builds.

#### Overview
Image lifecycle via MCP. Essential for container setup.

#### Key Tools
- `list_images`: List all. Params: manager_type?, silent?, log_file?.
- `pull_image`: Pull image/tag. Params: image (required), tag="latest", platform?.
- `remove_image`: Remove by name/ID. Params: image (required), force?.
- `prune_images`: Clean unused. Params: all?.

#### Usage Instructions
1. Parse image:tag; defaults to latest.
2. Chain: list -> pull -> run (from containers skill).

#### Examples
- Pull: `pull_image` with image="nginx", tag="latest".
- Prune: `prune_images` with all=true.

#### Error Handling
- Not found: Registry issues—check URL.
- In use: Use force or stop containers first.

### container-manager-mcp-info

**Description:** Retrieves Container Manager info. Use for version/system details before ops. Triggers - setup checks, compatibility.

#### Overview
Basic info tools for Docker/Podman. Call first to verify environment.

#### Key Tools
- `get_version`: Get manager version. Params: manager_type? (docker/podman), silent?, log_file?.
- `get_info`: Get system info (OS, drivers). Similar params.

#### Usage Instructions
1. Optional manager_type; auto-detects.
2. Use for troubleshooting setup issues.

#### Examples
- Version: `get_version` with manager_type="docker".
- Info: `get_info`.

#### Error Handling
- No manager: Check installation.
- Logs: Use log_file for persistence.

### container-manager-mcp-log

**Description:** Manages logs. Use for container/compose logs. Triggers - debugging, monitoring.

#### Overview
Log retrieval for troubleshooting.

#### Key Tools
- `get_container_logs`: Get logs. Params: container_id (required), tail="all".
- `compose_logs`: Compose logs. Params: compose_file (required), service?.

#### Usage Instructions
1. Tail for recent lines (e.g., "100").
2. Subset: Service-specific in compose.

#### Examples
- Container: `get_container_logs` with container_id="nginx", tail="50".
- Compose: `compose_logs` with compose_file="docker-compose.yml".

#### Error Handling
- No logs: Container not running.

### container-manager-mcp-network

**Description:** Manages networks. Use for listing/creating/removing/pruning. Triggers - isolation, connectivity.

#### Overview
Network isolation for containers.

#### Key Tools
- `list_networks`: List all.
- `create_network`: Create. Params: name (required), driver="bridge".
- `remove_network`: Remove. Params: network_id (required).
- `prune_networks`: Clean unused.

#### Usage Instructions
1. Default driver: bridge.

#### Examples
- Create: `create_network` with name="my-net".

#### Error Handling
- In use: Disconnect containers.

### container-manager-mcp-swarm

**Description:** Manages Docker Swarm. Use for init/leave, nodes/services. Triggers - clustering, orchestration. Note - Docker only.

#### Overview
Swarm for distributed ops. Restrict to Docker.

#### Key Tools
- `init_swarm`: Init cluster. Params: advertise_addr?.
- `leave_swarm`: Leave. Params: force?.
- `list_nodes`: List nodes.
- `list_services`: List services.
- `create_service`: Create. Params: name, image (required), replicas=1, ports?, mounts?.
- `remove_service`: Remove. Params: service_id (required).

#### Usage Instructions
1. Manager_type="docker" required.
2. For services: Similar to containers but replicated.

#### Examples
- Init: `init_swarm`.
- Create service: `create_service` with name="web", image="nginx", replicas=3.

#### Error Handling
- Not Swarm: Init first.
- Node down: Check status.
  Reference `orchestrate.md` for scaling workflows.

### container-manager-mcp-system

**Description:** Manages system resources. Use for full prune. Triggers - cleanup, optimization.

#### Overview
System-wide cleanup.

#### Key Tools
- `prune_system`: Prune all unused (containers/images/volumes/networks). Params: force?, all?.

#### Usage Instructions
1. Caution: Destructive—use force/all sparingly.

#### Examples
- Prune: `prune_system` with all=true.

#### Error Handling
- Partial failure: Check individual prunes.

### container-manager-mcp-volume

**Description:** Manages volumes. Use for listing/creating/removing/pruning. Triggers - data persistence.

#### Overview
Volume ops for stateful containers.

#### Key Tools
- `list_volumes`: List all.
- `create_volume`: Create. Params: name (required).
- `remove_volume`: Remove. Params: name (required), force?.
- `prune_volumes`: Clean unused. Params: all?.

#### Usage Instructions
1. Use with run_container volumes param.

#### Examples
- Create: `create_volume` with name="data-vol".
- Prune: `prune_volumes`.

#### Error Handling
- In use: Stop containers first.
