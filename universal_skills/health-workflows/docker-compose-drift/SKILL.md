---
name: docker-compose-drift
skill_type: workflow
description: >-
  Parallel execution workflow for docker compose drift using the Unified Parallel Engine
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
  tool_assignments:
    data-collector: [graph_query]
    analyzer-agent: [graph_analyze]
    planner-agent: [graph_write]
tags: [health, docker-compose-drift]
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.0.2'
---

# Docker Compose Drift Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for docker compose drift using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Stack Get File
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute fan out per stack get file operations for the Docker Compose Drift workflow.
Expected: `fan_out_per_stack_get_file_artifacts`

### Step 2: Compare Running State [depends_on: fan_out_per_stack_get_file]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute compare running state operations for the Docker Compose Drift workflow.
Expected: `compare_running_state_artifacts`

### Step 3: Drift Report [depends_on: compare_running_state]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute drift report operations for the Docker Compose Drift workflow.
Expected: `drift_report_artifacts`

### Step 4: KG Persistence [depends_on: drift_report]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Docker Compose Drift results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Stack Get File
- **After level 0:** Step 2 — Compare Running State
- **After level 1:** Step 3 — Drift Report
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
