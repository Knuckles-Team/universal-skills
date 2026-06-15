---
name: servicenow_incident_tracker
description: >-
  Fetch active ServiceNow incidents ordered with higher priority showing first
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
tags: [ops, servicenow-incident-tracker]
concept: CONCEPT:KG-2.12
---

# Servicenow Incident Tracker Workflow

**CONCEPT:KG-2.12**

Fetch active ServiceNow incidents ordered with higher priority showing first

## Steps

### Step 0: Servicenow Api
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Retrieve the list of active incidents using the `servicenow_incidents` action with `action='get_incidents'`. Pass `params_json` containing a query like `{"sysparm_query": "active=true^ORDERBYpriority"}` to ensure critical priority incidents appear first.

### Step 1: User Interaction
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Present the list of prioritized incidents to the user. Request selection of a specific incident for deeper inspection or action.

### Step 2: Servicenow Api
**Agent**: `validator-agent`
**Tools**: `graph_query`

Fetch full details for the selected incident ID using the `servicenow_incidents` action with `action='get_incident'` and the incident's sys_id.

### Step 3: User Interaction
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Display the comprehensive incident history, comments, SLA status, and proposed remediation plan to the user.

### Step 4: KG Persistence [depends_on: user-interaction]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Servicenow Incident Tracker results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Servicenow Api; Step 1 — User Interaction; Step 2 — Servicenow Api; Step 3 — User Interaction
- **After level 0:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
