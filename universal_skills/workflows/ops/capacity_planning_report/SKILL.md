---
name: capacity_planning_report
description: >-
  Parallel execution workflow for capacity planning report using the Unified Parallel Engine
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
tags: [ops, capacity-planning-report]
concept: CONCEPT:KG-2.12
---

# Capacity Planning Report Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for capacity planning report using the Unified Parallel Engine

## Steps

### Step 1: Velocity
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute velocity operations for the Capacity Planning Report workflow.
Expected: `velocity_artifacts`

### Step 2: Wip
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute wip operations for the Capacity Planning Report workflow.
Expected: `wip_artifacts`

### Step 3: Lead Time
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute lead time operations for the Capacity Planning Report workflow.
Expected: `lead_time_artifacts`

### Step 4: Forecast [depends_on: velocity, wip, lead_time]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute forecast operations for the Capacity Planning Report workflow.
Expected: `forecast_artifacts`

### Step 5: Report [depends_on: forecast]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute report operations for the Capacity Planning Report workflow.
Expected: `report_artifacts`

### Step 6: KG Persistence [depends_on: report]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Capacity Planning Report results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.
