---
name: multi-host-command-exec
skill_type: workflow
description: >-
  Parallel execution workflow for multi host command exec using the Unified Parallel Engine
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
  tool_assignments:
    scanner-agent: [tun_tm_system, tun_tm_remote]
    analyzer-agent: [graph_analyze, tun_tm_security]
    remediator-agent: [tun_tm_remote, tun_tm_inventory]
tags: [system, multi-host-command-exec]
concept: CONCEPT:SYS-001
metadata:
  version: '1.2.0'
---

# Multi Host Command Exec Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for multi host command exec using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Host Ssh Execute
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute fan out per host ssh execute operations for the Multi Host Command Exec workflow.
Expected: `fan_out_per_host_ssh_execute_artifacts`

### Step 2: Collect Output [depends_on: fan_out_per_host_ssh_execute]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute collect output operations for the Multi Host Command Exec workflow.
Expected: `collect_output_artifacts`

### Step 3: Aggregate [depends_on: collect_output]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute aggregate operations for the Multi Host Command Exec workflow.
Expected: `aggregate_artifacts`

### Step 4: KG Persistence [depends_on: aggregate]
**Agent**: `remediator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Multi Host Command Exec results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Host Ssh Execute
- **After level 0:** Step 2 — Collect Output
- **After level 1:** Step 3 — Aggregate
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
