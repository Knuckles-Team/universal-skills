---
name: training-program-builder
skill_type: workflow
description: >-
  Parallel execution workflow for training program builder using the Unified Parallel Engine
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
tags: [ops, training-program-builder]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.2.0'
---

# Training Program Builder Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for training program builder using the Unified Parallel Engine

## Steps

### Step 1: Skill Gap Analysis
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute skill gap analysis operations for the Training Program Builder workflow.
Expected: `skill_gap_analysis_artifacts`

### Step 2: Curate Content [depends_on: skill_gap_analysis]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute curate content operations for the Training Program Builder workflow.
Expected: `curate_content_artifacts`

### Step 3: Build Curriculum [depends_on: curate_content]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute build curriculum operations for the Training Program Builder workflow.
Expected: `build_curriculum_artifacts`

### Step 4: Schedule [depends_on: build_curriculum]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute schedule operations for the Training Program Builder workflow.
Expected: `schedule_artifacts`

### Step 5: Track [depends_on: schedule]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute track operations for the Training Program Builder workflow.
Expected: `track_artifacts`

### Step 6: KG Persistence [depends_on: track]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Training Program Builder results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Skill Gap Analysis
- **After level 0:** Step 2 — Curate Content
- **After level 1:** Step 3 — Build Curriculum
- **After level 2:** Step 4 — Schedule
- **After level 3:** Step 5 — Track
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
