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
