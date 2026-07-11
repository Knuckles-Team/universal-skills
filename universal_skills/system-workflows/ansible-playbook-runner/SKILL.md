---
name: ansible-playbook-runner
skill_type: workflow
description: >-
  Parallel execution workflow for ansible playbook runner using the Unified Parallel Engine
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
tags: [system, ansible-playbook-runner]
concept: CONCEPT:SYS-001
metadata:
  version: '1.2.0'
---

# Ansible Playbook Runner Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for ansible playbook runner using the Unified Parallel Engine

## Steps

### Step 1: Inventory Scan
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute inventory scan operations for the Ansible Playbook Runner workflow.
Expected: `inventory_scan_artifacts`

### Step 2: Playbook Select [depends_on: inventory_scan]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute playbook select operations for the Ansible Playbook Runner workflow.
Expected: `playbook_select_artifacts`

### Step 3: Execute [depends_on: playbook_select]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute execute operations for the Ansible Playbook Runner workflow.
Expected: `execute_artifacts`

### Step 4: Verify [depends_on: execute]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute verify operations for the Ansible Playbook Runner workflow.
Expected: `verify_artifacts`

### Step 5: KG Persistence [depends_on: verify]
**Agent**: `reporter-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Ansible Playbook Runner results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Inventory Scan
- **After level 0:** Step 2 — Playbook Select
- **After level 1:** Step 3 — Execute
- **After level 2:** Step 4 — Verify
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
