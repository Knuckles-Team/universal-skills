---
name: daily_health_dashboard
description: >-
  Parallel execution workflow for daily health dashboard using the Unified Parallel Engine
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
tags: [ops, daily-health-dashboard]
concept: CONCEPT:KG-2.12
---

# Daily Health Dashboard Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for daily health dashboard using the Unified Parallel Engine

## Steps

### Step 1: Sleep
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute sleep operations for the Daily Health Dashboard workflow.
Expected: `sleep_artifacts`

### Step 2: Exercise
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute exercise operations for the Daily Health Dashboard workflow.
Expected: `exercise_artifacts`

### Step 3: Nutrition
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute nutrition operations for the Daily Health Dashboard workflow.
Expected: `nutrition_artifacts`

### Step 4: Weight
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute weight operations for the Daily Health Dashboard workflow.
Expected: `weight_artifacts`

### Step 5: Trends [depends_on: sleep, exercise, nutrition, weight]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute trends operations for the Daily Health Dashboard workflow.
Expected: `trends_artifacts`

### Step 6: Recommendations [depends_on: trends]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute recommendations operations for the Daily Health Dashboard workflow.
Expected: `recommendations_artifacts`

### Step 7: KG Persistence [depends_on: recommendations]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Daily Health Dashboard results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.
