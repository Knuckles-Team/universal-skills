---
name: container-fleet-audit
skill_type: workflow
description: >-
  Parallel execution workflow for container fleet audit using the Unified Parallel Engine
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
tags: [health, container-fleet-audit]
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.0.2'
---

# Container Fleet Audit Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for container fleet audit using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Host List
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute fan out per host list operations for the Container Fleet Audit workflow.
Expected: `fan_out_per_host_list_artifacts`

### Step 2: Inspect Unhealthy [depends_on: fan_out_per_host_list]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute inspect unhealthy operations for the Container Fleet Audit workflow.
Expected: `inspect_unhealthy_artifacts`

### Step 3: Collect Logs [depends_on: inspect_unhealthy]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute collect logs operations for the Container Fleet Audit workflow.
Expected: `collect_logs_artifacts`

### Step 4: Remediate [depends_on: collect_logs]
**Agent**: `tracker-agent`
**Tools**: `nc_calendar, graph_write`

Execute remediate operations for the Container Fleet Audit workflow.
Expected: `remediate_artifacts`

### Step 5: KG Persistence [depends_on: remediate]
**Agent**: `tracker-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Container Fleet Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Host List
- **After level 0:** Step 2 — Inspect Unhealthy
- **After level 1:** Step 3 — Collect Logs
- **After level 2:** Step 4 — Remediate
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
