---
name: sales-pipeline-automation
skill_type: workflow
description: >-
  Parallel execution workflow for sales pipeline automation using the Unified Parallel Engine
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
tags: [ops, sales-pipeline-automation]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.0.2'
---

# Sales Pipeline Automation Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for sales pipeline automation using the Unified Parallel Engine

## Steps

### Step 1: Qualify Lead
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute qualify lead operations for the Sales Pipeline Automation workflow.
Expected: `qualify_lead_artifacts`

### Step 2: Demo Scheduling [depends_on: qualify_lead]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute demo scheduling operations for the Sales Pipeline Automation workflow.
Expected: `demo_scheduling_artifacts`

### Step 3: Proposal [depends_on: demo_scheduling]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute proposal operations for the Sales Pipeline Automation workflow.
Expected: `proposal_artifacts`

### Step 4: Follow Up [depends_on: proposal]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute follow up operations for the Sales Pipeline Automation workflow.
Expected: `follow_up_artifacts`

### Step 5: Close [depends_on: follow_up]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute close operations for the Sales Pipeline Automation workflow.
Expected: `close_artifacts`

### Step 6: KG Persistence [depends_on: close]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Sales Pipeline Automation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Qualify Lead
- **After level 0:** Step 2 — Demo Scheduling
- **After level 1:** Step 3 — Proposal
- **After level 2:** Step 4 — Follow Up
- **After level 3:** Step 5 — Close
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
