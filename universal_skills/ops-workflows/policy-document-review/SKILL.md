---
name: policy-document-review
skill_type: workflow
description: >-
  Parallel execution workflow for policy document review using the Unified Parallel Engine
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
tags: [ops, policy-document-review]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.2.0'
---

# Policy Document Review Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for policy document review using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Policy Check Currency
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute fan out per policy check currency operations for the Policy Document Review workflow.
Expected: `fan_out_per_policy_check_currency_artifacts`

### Step 2: Compare Regulations [depends_on: fan_out_per_policy_check_currency]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute compare regulations operations for the Policy Document Review workflow.
Expected: `compare_regulations_artifacts`

### Step 3: Update [depends_on: compare_regulations]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute update operations for the Policy Document Review workflow.
Expected: `update_artifacts`

### Step 4: Distribute [depends_on: update]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute distribute operations for the Policy Document Review workflow.
Expected: `distribute_artifacts`

### Step 5: KG Persistence [depends_on: distribute]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Policy Document Review results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Policy Check Currency
- **After level 0:** Step 2 — Compare Regulations
- **After level 1:** Step 3 — Update
- **After level 2:** Step 4 — Distribute
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
