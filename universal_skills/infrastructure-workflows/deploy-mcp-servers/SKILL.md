---
name: deploy-mcp-servers
skill_type: workflow
description: >-
  Parallel execution workflow for deploy mcp servers using the Unified Parallel Engine
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: infrastructure deployment and operations
  execution_mode: parallel
  specialist_ids:
    - discovery-agent
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
tags: [infra, deploy-mcp-servers]
concept: CONCEPT:INFRA-001
metadata:
  version: '1.1.0'
---

# Deploy Mcp Servers Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy mcp servers using the Unified Parallel Engine

## Steps

### Step 1: All 37 Mcp Server Containers  Waves
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute all 37 mcp server containers  waves operations for the Deploy Mcp Servers workflow.
Expected: `all_37_mcp_server_containers__waves_artifacts`

### Step 2: KG Persistence [depends_on: all_37_mcp_server_containers__waves]
**Agent**: `discovery-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Mcp Servers results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — All 37 Mcp Server Containers  Waves
- **After level 0:** Step 2 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
