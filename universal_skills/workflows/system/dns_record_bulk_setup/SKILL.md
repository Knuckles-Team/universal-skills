---
name: dns_record_bulk_setup
description: >-
  Parallel execution workflow for dns record bulk setup using the Unified Parallel Engine
domain: system
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
tags: [system, dns-record-bulk-setup]
concept: CONCEPT:SYS-001
---

# Dns Record Bulk Setup Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for dns record bulk setup using the Unified Parallel Engine

## Steps

### Step 1: Parse Service List
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute parse service list operations for the Dns Record Bulk Setup workflow.
Expected: `parse_service_list_artifacts`

### Step 2: Create Records [depends_on: parse_service_list]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute create records operations for the Dns Record Bulk Setup workflow.
Expected: `create_records_artifacts`

### Step 3: Verify Resolution [depends_on: create_records]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute verify resolution operations for the Dns Record Bulk Setup workflow.
Expected: `verify_resolution_artifacts`

### Step 4: KG Persistence [depends_on: verify_resolution]
**Agent**: `remediator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Dns Record Bulk Setup results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Parse Service List
- **After level 0:** Step 2 — Create Records
- **After level 1:** Step 3 — Verify Resolution
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
