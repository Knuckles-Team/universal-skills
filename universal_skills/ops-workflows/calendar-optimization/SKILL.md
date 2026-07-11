---
name: calendar-optimization
skill_type: workflow
description: >-
  Parallel execution workflow for calendar optimization using the Unified Parallel Engine
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
tags: [ops, calendar-optimization]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.2.0'
---

# Calendar Optimization Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for calendar optimization using the Unified Parallel Engine

## Steps

### Step 1: Scan Events
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute scan events operations for the Calendar Optimization workflow.
Expected: `scan_events_artifacts`

### Step 2: Find Conflicts [depends_on: scan_events]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute find conflicts operations for the Calendar Optimization workflow.
Expected: `find_conflicts_artifacts`

### Step 3: Suggest Rearrangements [depends_on: find_conflicts]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute suggest rearrangements operations for the Calendar Optimization workflow.
Expected: `suggest_rearrangements_artifacts`

### Step 4: Apply [depends_on: suggest_rearrangements]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute apply operations for the Calendar Optimization workflow.
Expected: `apply_artifacts`

### Step 5: KG Persistence [depends_on: apply]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Calendar Optimization results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Scan Events
- **After level 0:** Step 2 — Find Conflicts
- **After level 1:** Step 3 — Suggest Rearrangements
- **After level 2:** Step 4 — Apply
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
