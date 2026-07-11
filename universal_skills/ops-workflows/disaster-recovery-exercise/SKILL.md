---
name: disaster-recovery-exercise
skill_type: workflow
description: >-
  Parallel execution workflow for disaster recovery exercise using the Unified Parallel Engine
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
tags: [ops, disaster-recovery-exercise]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.2.0'
---

# Disaster Recovery Exercise Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for disaster recovery exercise using the Unified Parallel Engine

## Steps

### Step 1: Simulate Failure
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute simulate failure operations for the Disaster Recovery Exercise workflow.
Expected: `simulate_failure_artifacts`

### Step 2: Parallel Team Response [depends_on: simulate_failure]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute parallel team response operations for the Disaster Recovery Exercise workflow.
Expected: `parallel_team_response_artifacts`

### Step 3: Validate Recovery [depends_on: parallel_team_response]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute validate recovery operations for the Disaster Recovery Exercise workflow.
Expected: `validate_recovery_artifacts`

### Step 4: Debrief [depends_on: validate_recovery]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute debrief operations for the Disaster Recovery Exercise workflow.
Expected: `debrief_artifacts`

### Step 5: KG Persistence [depends_on: debrief]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Disaster Recovery Exercise results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Simulate Failure
- **After level 0:** Step 2 — Parallel Team Response
- **After level 1:** Step 3 — Validate Recovery
- **After level 2:** Step 4 — Debrief
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
