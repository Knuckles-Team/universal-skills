---
name: incident_management_lifecycle
description: >-
  Parallel execution workflow for incident management lifecycle using the Unified Parallel Engine
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
tags: [ops, incident-management-lifecycle]
concept: CONCEPT:KG-2.12
---

# Incident Management Lifecycle Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for incident management lifecycle using the Unified Parallel Engine

## Steps

### Step 1: Detect
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute detect operations for the Incident Management Lifecycle workflow.
Expected: `detect_artifacts`

### Step 2: Classify [depends_on: detect]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute classify operations for the Incident Management Lifecycle workflow.
Expected: `classify_artifacts`

### Step 3: Assign [depends_on: classify]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute assign operations for the Incident Management Lifecycle workflow.
Expected: `assign_artifacts`

### Step 4: Investigate [depends_on: assign]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute investigate operations for the Incident Management Lifecycle workflow.
Expected: `investigate_artifacts`

### Step 5: Resolve [depends_on: investigate]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute resolve operations for the Incident Management Lifecycle workflow.
Expected: `resolve_artifacts`

### Step 6: Postmortem [depends_on: resolve]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute postmortem operations for the Incident Management Lifecycle workflow.
Expected: `postmortem_artifacts`

### Step 7: KG Persistence [depends_on: postmortem]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Incident Management Lifecycle results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.
