---
name: change-request-pipeline
skill_type: workflow
description: >-
  Parallel execution workflow for change request pipeline using the Unified Parallel Engine
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
tags: [ops, change-request-pipeline]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.1.0'
---

# Change Request Pipeline Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for change request pipeline using the Unified Parallel Engine

## Steps

### Step 1: Submit
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute submit operations for the Change Request Pipeline workflow.
Expected: `submit_artifacts`

### Step 2: Review [depends_on: submit]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute review operations for the Change Request Pipeline workflow.
Expected: `review_artifacts`

### Step 3: Approve [depends_on: review]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute approve operations for the Change Request Pipeline workflow.
Expected: `approve_artifacts`

### Step 4: Implement [depends_on: approve]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute implement operations for the Change Request Pipeline workflow.
Expected: `implement_artifacts`

### Step 5: Verify [depends_on: implement]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute verify operations for the Change Request Pipeline workflow.
Expected: `verify_artifacts`

### Step 6: Close [depends_on: verify]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute close operations for the Change Request Pipeline workflow.
Expected: `close_artifacts`

### Step 7: KG Persistence [depends_on: close]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Change Request Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Submit
- **After level 0:** Step 2 — Review
- **After level 1:** Step 3 — Approve
- **After level 2:** Step 4 — Implement
- **After level 3:** Step 5 — Verify
- **After level 4:** Step 6 — Close
- **After level 5:** Step 7 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
