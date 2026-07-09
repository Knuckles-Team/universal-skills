---
name: resource-usage-forecast
skill_type: workflow
description: >-
  Parallel execution workflow for resource usage forecast using the Unified Parallel Engine
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
tags: [health, resource-usage-forecast]
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.1.0'
---

# Resource Usage Forecast Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for resource usage forecast using the Unified Parallel Engine

## Steps

### Step 1: Collect Cpu Mem Disk Per Host
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute collect cpu mem disk per host operations for the Resource Usage Forecast workflow.
Expected: `collect_cpu_mem_disk_per_host_artifacts`

### Step 2: Trend Analysis [depends_on: collect_cpu_mem_disk_per_host]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute trend analysis operations for the Resource Usage Forecast workflow.
Expected: `trend_analysis_artifacts`

### Step 3: Capacity Report [depends_on: trend_analysis]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute capacity report operations for the Resource Usage Forecast workflow.
Expected: `capacity_report_artifacts`

### Step 4: KG Persistence [depends_on: capacity_report]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Resource Usage Forecast results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Collect Cpu Mem Disk Per Host
- **After level 0:** Step 2 — Trend Analysis
- **After level 1:** Step 3 — Capacity Report
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
