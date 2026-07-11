---
name: bedtime-routine-orchestrator
skill_type: workflow
description: >-
  Parallel execution workflow for bedtime routine orchestrator using the Unified Parallel Engine
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
tags: [ops, bedtime-routine-orchestrator]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.2.0'
---

# Bedtime Routine Orchestrator Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for bedtime routine orchestrator using the Unified Parallel Engine

## Steps

### Step 1: Lights Dim
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute lights dim operations for the Bedtime Routine Orchestrator workflow.
Expected: `lights_dim_artifacts`

### Step 2: Thermostat Down
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute thermostat down operations for the Bedtime Routine Orchestrator workflow.
Expected: `thermostat_down_artifacts`

### Step 3: Locks Check
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute locks check operations for the Bedtime Routine Orchestrator workflow.
Expected: `locks_check_artifacts`

### Step 4: Alarm Set
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute alarm set operations for the Bedtime Routine Orchestrator workflow.
Expected: `alarm_set_artifacts`

### Step 5: Report [depends_on: lights_dim, thermostat_down, locks_check, alarm_set]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute report operations for the Bedtime Routine Orchestrator workflow.
Expected: `report_artifacts`

### Step 6: KG Persistence [depends_on: report]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Bedtime Routine Orchestrator results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Lights Dim; Step 2 — Thermostat Down; Step 3 — Locks Check; Step 4 — Alarm Set
- **After level 0:** Step 5 — Report
- **After level 1:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
