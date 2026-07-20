---
name: servicenow-trm-tracker
skill_type: workflow
description: >-
  Fetch active ServiceNow TRM (Technology Reference Model) Requests
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
tags: [ops, servicenow-trm-tracker]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.2.1'
---

# Servicenow Trm Tracker Workflow

**CONCEPT:KG-2.12**

Fetch active ServiceNow TRM (Technology Reference Model) Requests

## Steps

### Step 0: ServiceNow TRM-Queue Query [skill: servicenow-api]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Query the ServiceNow TRM requests table (typically `u_trm_request` or relevant `dmn_demand` table) using the `servicenow_table_api` action with `action='get_table'`. Order by creation date descending via `params_json` containing a query like `{"sysparm_query": "active=true^ORDERBYdescsys_created_on", "sysparm_limit": 20}`.

### Step 1: TRM-Selection Interaction [skill: user-interaction]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Present the latest TRM compliance evaluation queue to the user. Prompt them to select a request for deep tech stack compliance analysis.

### Step 2: ServiceNow TRM-Record Inspection [skill: servicenow-api]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Fetch full fields and developer requirements for the selected TRM record using `servicenow_table_api` with `action='get_table_record'`.

### Step 3: TRM-Assessment Presentation [skill: user-interaction]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Display the architecture evaluation logs, software categories status, and next assessment workflow steps to the user.

### Step 4: KG Persistence [depends_on: Step 3]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Servicenow Trm Tracker results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — ServiceNow TRM-Queue Query; Step 1 — TRM-Selection Interaction; Step 2 — ServiceNow TRM-Record Inspection; Step 3 — TRM-Assessment Presentation
- **After level 0:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
