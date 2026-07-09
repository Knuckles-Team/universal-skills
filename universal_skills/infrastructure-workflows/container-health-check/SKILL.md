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
  version: '1.1.0'
---

# Container Health Check Workflow

**CONCEPT:INFRA-001**

Full Docker infrastructure health assessment. Lists containers, images, volumes, and networks, then retrieves logs from a running container.

## Steps

### Step 0: Container Manager Mcp
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

List all running containers and their current status
Expected: `container, running, status`

### Step 1: Container Manager Mcp
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

List all Docker images with their sizes and tags
Expected: `image, tag`

### Step 2: Container Manager Mcp
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Show all Docker volumes and networks
Expected: `volume, network`

### Step 3: Container Manager Mcp
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Get the logs for one of the running containers
Expected: `log`

### Step 4: KG Persistence [depends_on: container-manager-mcp]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Container Health Check results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Container Manager Mcp; Step 1 — Container Manager Mcp; Step 2 — Container Manager Mcp; Step 3 — Container Manager Mcp
- **After level 0:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
