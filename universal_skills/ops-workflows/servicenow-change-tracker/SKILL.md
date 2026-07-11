---
name: servicenow-change-tracker
skill_type: workflow
description: >-
  Fetch active ServiceNow Change Requests sorted chronologically
domain: ops-workflows
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
tags: [ops, servicenow-change-tracker]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.2.0'
---

# Servicenow Change Tracker Workflow

**CONCEPT:KG-2.12**

Fetch active ServiceNow Change Requests sorted chronologically

## Steps

### Step 0: Servicenow Api
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Retrieve a list of active change requests using the `servicenow_change_management` action with `action='get_change_requests'`. Specify a chronological descending query via `params_json` (e.g. `{"sysparm_query": "active=true^ORDERBYdescsys_created_on"}`).

### Step 1: User Interaction
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Display the chronological change log and scheduled maintenance windows to the user. Ask if they wish to inspect a specific change ticket or analyze scheduling conflicts.

### Step 2: Servicenow Api
**Agent**: `validator-agent`
**Tools**: `graph_query`

Retrieve comprehensive details for the selected change request ID using `servicenow_change_management` with `action='get_change_request'` and `action='get_change_request_conflict'` to detect environmental schedule clashes.

### Step 3: User Interaction
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Present the detailed change payload, risk factors, conflict scan report, and approval paths to the user.

### Step 4: KG Persistence [depends_on: user-interaction]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Servicenow Change Tracker results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Servicenow Api; Step 1 — User Interaction; Step 2 — Servicenow Api; Step 3 — User Interaction
- **After level 0:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
