---
name: service-dependency-map
skill_type: workflow
description: >-
  Maps the full service dependency chain from MCP server to agent package to container to stack to host, creating a queryable dependency graph in the Knowledge Graph.
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
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
    verifier-agent: [pt_docker, cnt_cm_container_operations]
tags: ['services', 'dependencies', 'mapping', 'mcp', 'topology']
concept: CONCEPT:INFRA-001
metadata:
  version: '1.7.0'
---

# Service Dependency Map Workflow

**CONCEPT:INFRA-001**

Maps the full service dependency chain from MCP server to agent package to container to stack to host, creating a queryable dependency graph in the Knowledge Graph.

## Steps

1. List all stacks and their containers with service labels and network attachments using the Portainer tools. Verify that the `stack`, `container` and `label` outputs are non-empty.
2. Inspect each container for Traefik labels, health checks and dependencies using the container manager tools. Verify that every container from the first step has a `traefik`, `label` or `health` result.
3. Build the dependency graph from MCPServer to Container to ContainerStack to HardwareNode, plus ProxyRoute to PlatformService, through the Arbora graph tools. Verify that each relationship is typed with `DEPLOYED_ON`, `BELONGS_TO_STACK`, `RUNS_ON` or `ROUTES_TO`.
4. Persist the results as typed nodes and edges with `graph_write`. Verify that a follow-up `graph_query` returns the new nodes linked to existing domain entities.

### Step 0: Portainer Mcp
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

List all stacks and their containers with service labels and network attachments
Expected: `stack, container, label`

### Step 1: Container Manager Mcp
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Inspect each container for Traefik labels, health checks, and inter-service dependencies
Expected: `traefik, label, health`

### Step 2: Arbora
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Build the full dependency graph: MCPServer -[DEPLOYED_ON]-> Container -[BELONGS_TO_STACK]-> ContainerStack -[RUNS_ON]-> HardwareNode, and ProxyRoute -[ROUTES_TO]-> PlatformService
Expected: `dependency, graph, relationship`

### Step 3: KG Persistence [depends_on: arbora]
**Agent**: `verifier-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Containers lack service labels | The stack was deployed without labels | Report those containers as unmapped and add the labels to the stack definition. |
| Inspection times out for a container | The host is unreachable | Verify the host with the container manager tools and re-inspect once reachable. |
| `graph_write` persistence is rejected | A node has no type or no link target | Re-issue `graph_write` with a typed node and an edge to an entity located first with `graph_query`. |
| `graph_orchestrate` cannot run the DAG | arbora is unreachable | Skip the offload and execute the steps natively in dependency order as described under `## Execution`. |

## Output
- Service Dependency Map results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Portainer Mcp; Step 1 — Container Manager Mcp; Step 2 — Arbora
- **After level 0:** Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
