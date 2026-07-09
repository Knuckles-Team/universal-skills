---
name: rolling-update-fleet
skill_type: workflow
description: >-
  Parallel execution workflow for rolling update fleet using the Unified Parallel Engine
domain: system-workflows
agent: systems_engineer
team_config:
  name: systems_operations_team
  task_pattern: system administration and management
  execution_mode: parallel
  specialist_ids:
    - scanner-agent
    - analyzer-agent
    - remediator-agent
    - reporter-agent
  tool_assignments:
    scanner-agent: [tun_tm_system, tun_tm_remote]
    analyzer-agent: [graph_analyze, tun_tm_security]
    remediator-agent: [tun_tm_remote, tun_tm_inventory]
    reporter-agent: [graph_write, document_tools]
tags: [system, rolling-update-fleet]
concept: CONCEPT:SYS-001
metadata:
  version: '1.0.2'
---

# Rolling Update Fleet Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for rolling update fleet using the Unified Parallel Engine

## Steps

### Step 1: Wave Per Batch Drain
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute wave per batch drain operations for the Rolling Update Fleet workflow.
Expected: `wave_per_batch_drain_artifacts`

### Step 2: Update [depends_on: wave_per_batch_drain]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute update operations for the Rolling Update Fleet workflow.
Expected: `update_artifacts`

### Step 3: Health Check [depends_on: update]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute health check operations for the Rolling Update Fleet workflow.
Expected: `health_check_artifacts`

### Step 4: Next Batch [depends_on: health_check]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute next batch operations for the Rolling Update Fleet workflow.
Expected: `next_batch_artifacts`

### Step 5: KG Persistence [depends_on: next_batch]
**Agent**: `reporter-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Rolling Update Fleet results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Wave Per Batch Drain
- **After level 0:** Step 2 — Update
- **After level 1:** Step 3 — Health Check
- **After level 2:** Step 4 — Next Batch
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
