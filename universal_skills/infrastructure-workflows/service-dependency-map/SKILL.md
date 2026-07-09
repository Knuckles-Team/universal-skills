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
  version: '1.1.0'
---

# Service Dependency Map Workflow

**CONCEPT:INFRA-001**

Maps the full service dependency chain from MCP server to agent package to container to stack to host, creating a queryable dependency graph in the Knowledge Graph.

## Steps

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

### Step 2: Graph Os
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Build the full dependency graph: MCPServer -[DEPLOYED_ON]-> Container -[BELONGS_TO_STACK]-> ContainerStack -[RUNS_ON]-> HardwareNode, and ProxyRoute -[ROUTES_TO]-> PlatformService
Expected: `dependency, graph, relationship`

### Step 3: KG Persistence [depends_on: graph-os]
**Agent**: `verifier-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Service Dependency Map results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Portainer Mcp; Step 1 — Container Manager Mcp; Step 2 — Graph Os
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
