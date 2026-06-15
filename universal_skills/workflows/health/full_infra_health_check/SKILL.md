---
name: full_infra_health_check
description: >-
  Parallel execution workflow for full infra health check using the Unified Parallel Engine
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
tags: [health, full-infra-health-check]
concept: CONCEPT:HEALTH-001
---

# Full Infra Health Check Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for full infra health check using the Unified Parallel Engine

## Steps

### Step 1: Containers
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute containers operations for the Full Infra Health Check workflow.
Expected: `containers_artifacts`

### Step 2: Dns
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute dns operations for the Full Infra Health Check workflow.
Expected: `dns_artifacts`

### Step 3: Uptime
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute uptime operations for the Full Infra Health Check workflow.
Expected: `uptime_artifacts`

### Step 4: Disks
**Agent**: `tracker-agent`
**Tools**: `nc_calendar, graph_write`

Execute disks operations for the Full Infra Health Check workflow.
Expected: `disks_artifacts`

### Step 5: Memory
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute memory operations for the Full Infra Health Check workflow.
Expected: `memory_artifacts`

### Step 6: KG Persistence [depends_on: memory]
**Agent**: `tracker-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Full Infra Health Check results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Containers; Step 2 — Dns; Step 3 — Uptime; Step 4 — Disks; Step 5 — Memory
- **After level 0:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
