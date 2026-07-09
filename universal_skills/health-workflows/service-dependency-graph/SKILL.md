---
name: service-dependency-graph
description: >-
  Parallel execution workflow for service dependency graph using the Unified Parallel Engine
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
tags: [health, service-dependency-graph]
concept: CONCEPT:HEALTH-001
---

# Service Dependency Graph Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for service dependency graph using the Unified Parallel Engine

## Steps

### Step 1: Scan All Containers
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute scan all containers operations for the Service Dependency Graph workflow.
Expected: `scan_all_containers_artifacts`

### Step 2: Extract Env Vars [depends_on: scan_all_containers]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute extract env vars operations for the Service Dependency Graph workflow.
Expected: `extract_env_vars_artifacts`

### Step 3: Build Dep Graph [depends_on: extract_env_vars]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute build dep graph operations for the Service Dependency Graph workflow.
Expected: `build_dep_graph_artifacts`

### Step 4: Kg Ingest [depends_on: build_dep_graph]
**Agent**: `tracker-agent`
**Tools**: `nc_calendar, graph_write`

Execute kg ingest operations for the Service Dependency Graph workflow.
Expected: `kg_ingest_artifacts`

## Output
- Service Dependency Graph results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Scan All Containers
- **After level 0:** Step 2 — Extract Env Vars
- **After level 1:** Step 3 — Build Dep Graph
- **After level 2:** Step 4 — Kg Ingest

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
