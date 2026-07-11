---
name: log-rotation-setup
skill_type: workflow
description: >-
  Parallel execution workflow for log rotation setup using the Unified Parallel Engine
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
tags: [system, log-rotation-setup]
concept: CONCEPT:SYS-001
metadata:
  version: '1.2.0'
---

# Log Rotation Setup Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for log rotation setup using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Service Configure Logrotate
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute fan out per service configure logrotate operations for the Log Rotation Setup workflow.
Expected: `fan_out_per_service_configure_logrotate_artifacts`

### Step 2: Test [depends_on: fan_out_per_service_configure_logrotate]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute test operations for the Log Rotation Setup workflow.
Expected: `test_artifacts`

### Step 3: Verify [depends_on: test]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute verify operations for the Log Rotation Setup workflow.
Expected: `verify_artifacts`

### Step 4: KG Persistence [depends_on: verify]
**Agent**: `remediator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Log Rotation Setup results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Service Configure Logrotate
- **After level 0:** Step 2 — Test
- **After level 1:** Step 3 — Verify
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
