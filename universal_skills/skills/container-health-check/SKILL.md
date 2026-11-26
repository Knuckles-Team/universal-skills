---
name: container-health-check
skill_type: workflow
description: >-
  Full Docker infrastructure health assessment. Lists containers, images, volumes, and networks, then retrieves logs from a running container.
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: infrastructure deployment and operations
  execution_mode: parallel
  specialist_ids:
    - discovery-agent
    - deployer-agent
    - verifier-agent
    - dns-configurator
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
    verifier-agent: [pt_docker, cnt_cm_container_operations]
    dns-configurator: [adg_rewrites, td_zones]
tags: ['docker', 'health', 'monitoring', 'containers']
concept: CONCEPT:INFRA-001
metadata:
  version: '1.6.2'
---

# Container Health Check Workflow

**CONCEPT:INFRA-001**

Full Docker infrastructure health assessment. Lists containers, images, volumes, and networks, then retrieves logs from a running container.

## Steps

1. List all running containers with their status via `container-manager-mcp` (Step 0). Verify that the output includes a `container` name and `status` for each entry.
2. List all Docker images with sizes and tags (Step 1). Verify that every row carries an `image` and a `tag`.
3. List the Docker volumes and networks (Step 2). Verify that both a `volume` list and a `network` list are returned.
4. Fetch the logs of one running container via `container-manager-mcp` (Step 3). Verify that the output contains log lines for the named container.
5. Persist the findings with `graph_write` (Step 4). Verify that `graph_query` returns the stored health-check node.

### Step 0: list-containers [skill: container-manager-mcp]
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

List all running containers and their current status
Expected: `container, running, status`

### Step 1: list-images [skill: container-manager-mcp]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

List all Docker images with their sizes and tags
Expected: `image, tag`

### Step 2: list-storage-and-networks [skill: container-manager-mcp]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Show all Docker volumes and networks
Expected: `volume, network`

### Step 3: fetch-container-logs [skill: container-manager-mcp]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Get the logs for one of the running containers
Expected: `log`

### Step 4: KG Persistence [depends_on: Step 0, Step 1, Step 2, Step 3]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Container list is empty | The tool points at the wrong Docker context or host | Run `docker context ls`, select the right context, and rerun Step 0 against it |
| Log fetch returns nothing | The chosen container is stopped or produces no output | Pick a running container from the Step 0 list and call Step 3 again with its name |
| `graph_write` fails | arbora is unreachable | Confirm access with `graph_query` and resubmit Step 4 once it responds |


## Output
- Container Health Check results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — list-containers; Step 1 — list-images; Step 2 — list-storage-and-networks; Step 3 — fetch-container-logs
- **After level 0:** Step 4 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
