---
name: enterprise_full_audit
description: >-
  Parallel execution workflow for enterprise full audit using the Unified Parallel Engine
domain: ops
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
tags: [ops, enterprise-full-audit]
concept: CONCEPT:KG-2.12
---

# Enterprise Full Audit Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for enterprise full audit using the Unified Parallel Engine

## Steps

### Step 1: Ceo
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute ceo operations for the Enterprise Full Audit workflow.
Expected: `ceo_artifacts`

### Step 2: 8 Dept Heads [depends_on: ceo]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute 8 dept heads operations for the Enterprise Full Audit workflow.
Expected: `8_dept_heads_artifacts`

### Step 3: Step 2 0 [depends_on: 8_dept_heads]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute step 2 0 operations for the Enterprise Full Audit workflow.
Expected: `step_2_0_artifacts`

### Step 4: Specialists [depends_on: 8_dept_heads]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute specialists operations for the Enterprise Full Audit workflow.
Expected: `specialists_artifacts`

### Step 5: KG Persistence [depends_on: specialists]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Enterprise Full Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Ceo
- **After level 0:** Step 2 — 8 Dept Heads
- **After level 1:** Step 3 — Step 2 0; Step 4 — Specialists
- **After level 2:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
