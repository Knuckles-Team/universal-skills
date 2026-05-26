---
name: resource_usage_forecast
description: >-
  Parallel execution workflow for resource usage forecast using the Unified Parallel Engine
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
  tool_assignments:
    data-collector: [graph_query]
    analyzer-agent: [graph_analyze]
    planner-agent: [graph_write]
tags: [health, resource-usage-forecast]
concept: CONCEPT:HEALTH-001
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
