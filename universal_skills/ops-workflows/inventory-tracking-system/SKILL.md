---
name: inventory-tracking-system
skill_type: workflow
description: >-
  Parallel execution workflow for inventory tracking system using the Unified Parallel Engine
domain: ops-workflows
agent: operations_coordinator
team_config:
  name: operations_team
  task_pattern: operational process coordination
  execution_mode: sequential
  specialist_ids:
    - intake-agent
    - processor-agent
    - validator-agent
    - report-agent
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
    validator-agent: [graph_query]
    report-agent: [graph_write, document_tools]
tags: [ops, inventory-tracking-system]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.1.0'
---

# Inventory Tracking System Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for inventory tracking system using the Unified Parallel Engine

## Steps

### Step 1: Count
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute count operations for the Inventory Tracking System workflow.
Expected: `count_artifacts`

### Step 2: Compare Expected [depends_on: count]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute compare expected operations for the Inventory Tracking System workflow.
Expected: `compare_expected_artifacts`

### Step 3: Flag Discrepancies [depends_on: compare_expected]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute flag discrepancies operations for the Inventory Tracking System workflow.
Expected: `flag_discrepancies_artifacts`

### Step 4: Reorder [depends_on: flag_discrepancies]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute reorder operations for the Inventory Tracking System workflow.
Expected: `reorder_artifacts`

### Step 5: KG Persistence [depends_on: reorder]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Inventory Tracking System results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Count
- **After level 0:** Step 2 — Compare Expected
- **After level 1:** Step 3 — Flag Discrepancies
- **After level 2:** Step 4 — Reorder
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
