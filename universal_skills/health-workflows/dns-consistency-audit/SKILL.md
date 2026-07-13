---
name: dns-consistency-audit
skill_type: workflow
description: >-
  Parallel execution workflow for dns consistency audit using the Unified Parallel Engine
domain: health-workflows
agent: health_wellness_coordinator
team_config:
  name: health_wellness_team
  task_pattern: health monitoring and wellness optimization
  execution_mode: sequential
  specialist_ids:
    - data-collector
    - analyzer-agent
    - planner-agent
    - tracker-agent
  tool_assignments:
    data-collector: [graph_query]
    analyzer-agent: [graph_analyze]
    planner-agent: [graph_write]
    tracker-agent: [nc_calendar, graph_write]
tags: [health, dns-consistency-audit]
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.2.1'
---

# Dns Consistency Audit Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for dns consistency audit using the Unified Parallel Engine

## Steps

### Step 1: List Records
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute list records operations for the Dns Consistency Audit workflow.
Expected: `list_records_artifacts`

### Step 2: Resolve Each
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute resolve each operations for the Dns Consistency Audit workflow.
Expected: `resolve_each_artifacts`

### Step 3: Compare
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute compare operations for the Dns Consistency Audit workflow.
Expected: `compare_artifacts`

### Step 4: Drift Report [depends_on: list_records, resolve_each, compare]
**Agent**: `tracker-agent`
**Tools**: `nc_calendar, graph_write`

Execute drift report operations for the Dns Consistency Audit workflow.
Expected: `drift_report_artifacts`

### Step 5: KG Persistence [depends_on: drift_report]
**Agent**: `tracker-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Dns Consistency Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — List Records; Step 2 — Resolve Each; Step 3 — Compare
- **After level 0:** Step 4 — Drift Report
- **After level 1:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
