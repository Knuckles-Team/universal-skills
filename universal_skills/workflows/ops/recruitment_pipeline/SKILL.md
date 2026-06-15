---
name: recruitment_pipeline
description: >-
  Parallel execution workflow for recruitment pipeline using the Unified Parallel Engine
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
tags: [ops, recruitment-pipeline]
concept: CONCEPT:KG-2.12
---

# Recruitment Pipeline Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for recruitment pipeline using the Unified Parallel Engine

## Steps

### Step 1: Post Job
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute post job operations for the Recruitment Pipeline workflow.
Expected: `post_job_artifacts`

### Step 2: Screen Resumes [depends_on: post_job]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute screen resumes operations for the Recruitment Pipeline workflow.
Expected: `screen_resumes_artifacts`

### Step 3: Schedule Interviews [depends_on: screen_resumes]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute schedule interviews operations for the Recruitment Pipeline workflow.
Expected: `schedule_interviews_artifacts`

### Step 4: Evaluate [depends_on: schedule_interviews]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute evaluate operations for the Recruitment Pipeline workflow.
Expected: `evaluate_artifacts`

### Step 5: Offer [depends_on: evaluate]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute offer operations for the Recruitment Pipeline workflow.
Expected: `offer_artifacts`

### Step 6: KG Persistence [depends_on: offer]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Recruitment Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Post Job
- **After level 0:** Step 2 — Screen Resumes
- **After level 1:** Step 3 — Schedule Interviews
- **After level 2:** Step 4 — Evaluate
- **After level 3:** Step 5 — Offer
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
