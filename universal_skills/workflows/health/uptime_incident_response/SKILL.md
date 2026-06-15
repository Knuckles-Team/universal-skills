---
name: uptime_incident_response
description: >-
  Parallel execution workflow for uptime incident response using the Unified Parallel Engine
domain: health
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
tags: [health, uptime-incident-response]
concept: CONCEPT:HEALTH-001
---

# Uptime Incident Response Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for uptime incident response using the Unified Parallel Engine

## Steps

### Step 1: Detect Down
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute detect down operations for the Uptime Incident Response workflow.
Expected: `detect_down_artifacts`

### Step 2: Diagnose [depends_on: detect_down]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute diagnose operations for the Uptime Incident Response workflow.
Expected: `diagnose_artifacts`

### Step 3: Restart [depends_on: diagnose]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute restart operations for the Uptime Incident Response workflow.
Expected: `restart_artifacts`

### Step 4: Verify [depends_on: restart]
**Agent**: `tracker-agent`
**Tools**: `nc_calendar, graph_write`

Execute verify operations for the Uptime Incident Response workflow.
Expected: `verify_artifacts`

### Step 5: Notify [depends_on: verify]
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute notify operations for the Uptime Incident Response workflow.
Expected: `notify_artifacts`

### Step 6: KG Persistence [depends_on: notify]
**Agent**: `tracker-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Uptime Incident Response results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Detect Down
- **After level 0:** Step 2 — Diagnose
- **After level 1:** Step 3 — Restart
- **After level 2:** Step 4 — Verify
- **After level 3:** Step 5 — Notify
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
