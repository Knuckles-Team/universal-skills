---
name: container-resource-limits
description: >-
  Parallel execution workflow for container resource limits using the Unified Parallel Engine
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
    - reporter-agent
  tool_assignments:
    scanner-agent: [tun_tm_system, tun_tm_remote]
    analyzer-agent: [graph_analyze, tun_tm_security]
    remediator-agent: [tun_tm_remote, tun_tm_inventory]
    reporter-agent: [graph_write, document_tools]
tags: [system, container-resource-limits]
concept: CONCEPT:SYS-001
---

# Container Resource Limits Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for container resource limits using the Unified Parallel Engine

## Steps

### Step 1: Inspect All
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute inspect all operations for the Container Resource Limits workflow.
Expected: `inspect_all_artifacts`

### Step 2: Identify Unlimited [depends_on: inspect_all]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute identify unlimited operations for the Container Resource Limits workflow.
Expected: `identify_unlimited_artifacts`

### Step 3: Apply Policies [depends_on: identify_unlimited]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute apply policies operations for the Container Resource Limits workflow.
Expected: `apply_policies_artifacts`

### Step 4: Verify [depends_on: apply_policies]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute verify operations for the Container Resource Limits workflow.
Expected: `verify_artifacts`

### Step 5: KG Persistence [depends_on: verify]
**Agent**: `reporter-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Container Resource Limits results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Inspect All
- **After level 0:** Step 2 — Identify Unlimited
- **After level 1:** Step 3 — Apply Policies
- **After level 2:** Step 4 — Verify
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
