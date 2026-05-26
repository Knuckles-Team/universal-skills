---
name: morning_briefing
description: >-
  Parallel execution workflow for morning briefing using the Unified Parallel Engine
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
tags: [ops, morning-briefing]
concept: CONCEPT:KG-2.12
---

# Morning Briefing Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for morning briefing using the Unified Parallel Engine

## Steps

### Step 1: Calendar
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute calendar operations for the Morning Briefing workflow.
Expected: `calendar_artifacts`

### Step 2: Weather
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute weather operations for the Morning Briefing workflow.
Expected: `weather_artifacts`

### Step 3: News
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute news operations for the Morning Briefing workflow.
Expected: `news_artifacts`

### Step 4: Inbox
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute inbox operations for the Morning Briefing workflow.
Expected: `inbox_artifacts`

### Step 5: Tasks
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute tasks operations for the Morning Briefing workflow.
Expected: `tasks_artifacts`

### Step 6: Digest [depends_on: calendar, weather, news, inbox, tasks]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute digest operations for the Morning Briefing workflow.
Expected: `digest_artifacts`

### Step 7: KG Persistence [depends_on: digest]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Morning Briefing results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.
