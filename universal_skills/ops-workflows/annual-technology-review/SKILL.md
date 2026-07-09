---
name: annual-technology-review
skill_type: workflow
description: >-
  Parallel execution workflow for annual technology review using the Unified Parallel Engine
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
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
    validator-agent: [graph_query]
tags: [ops, annual-technology-review]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.0.2'
---

# Annual Technology Review Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for annual technology review using the Unified Parallel Engine

## Steps

### Step 1: Evaluate
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute evaluate operations for the Annual Technology Review workflow.
Expected: `evaluate_artifacts`

### Step 2: Compare Alternatives [depends_on: evaluate]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute compare alternatives operations for the Annual Technology Review workflow.
Expected: `compare_alternatives_artifacts`

### Step 3: Migration Plan [depends_on: compare_alternatives]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute migration plan operations for the Annual Technology Review workflow.
Expected: `migration_plan_artifacts`

### Step 4: KG Persistence [depends_on: migration_plan]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Annual Technology Review results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Evaluate
- **After level 0:** Step 2 — Compare Alternatives
- **After level 1:** Step 3 — Migration Plan
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
