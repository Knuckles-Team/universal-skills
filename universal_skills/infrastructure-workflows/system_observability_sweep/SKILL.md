---
name: system_observability_sweep
description: >-
  Cross-system health and resource check combining system metrics with Langfuse observability status.
domain: infra
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
tags: ['monitoring', 'health', 'cross-system', 'observability']
concept: CONCEPT:INFRA-001
---

# System Observability Sweep Workflow

**CONCEPT:INFRA-001**

Cross-system health and resource check combining system metrics with Langfuse observability status.

## Steps

### Step 0: Systems Manager
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Get the system memory usage, CPU stats, and disk utilization
Expected: `memory, cpu`

### Step 1: Langfuse Mcp
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Check the Langfuse health endpoint and list all current datasets
Expected: `health, dataset`

### Step 2: Langfuse Mcp
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

List the most recent traces and their status
Expected: `trace`

### Step 3: KG Persistence [depends_on: langfuse-mcp]
**Agent**: `verifier-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- System Observability Sweep results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Systems Manager; Step 1 — Langfuse Mcp; Step 2 — Langfuse Mcp
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
