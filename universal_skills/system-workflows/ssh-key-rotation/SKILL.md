---
name: ssh-key-rotation
skill_type: workflow
description: >-
  Parallel execution workflow for ssh key rotation using the Unified Parallel Engine
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
tags: [system, ssh-key-rotation]
concept: CONCEPT:SYS-001
metadata:
  version: '1.1.0'
---

# Ssh Key Rotation Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for ssh key rotation using the Unified Parallel Engine

## Steps

### Step 1: Generate New Keys
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute generate new keys operations for the Ssh Key Rotation workflow.
Expected: `generate_new_keys_artifacts`

### Step 2: Distribute [depends_on: generate_new_keys]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute distribute operations for the Ssh Key Rotation workflow.
Expected: `distribute_artifacts`

### Step 3: Update Configs [depends_on: distribute]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute update configs operations for the Ssh Key Rotation workflow.
Expected: `update_configs_artifacts`

### Step 4: Revoke Old [depends_on: update_configs]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute revoke old operations for the Ssh Key Rotation workflow.
Expected: `revoke_old_artifacts`

### Step 5: KG Persistence [depends_on: revoke_old]
**Agent**: `reporter-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Ssh Key Rotation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Generate New Keys
- **After level 0:** Step 2 — Distribute
- **After level 1:** Step 3 — Update Configs
- **After level 2:** Step 4 — Revoke Old
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
