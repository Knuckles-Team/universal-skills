---
name: cross_team_dependency_tracker
description: >-
  Parallel execution workflow for cross team dependency tracker using the Unified Parallel Engine
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
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
    validator-agent: [graph_query]
tags: [ops, cross-team-dependency-tracker]
concept: CONCEPT:KG-2.12
---

# Cross Team Dependency Tracker Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for cross team dependency tracker using the Unified Parallel Engine

## Steps

### Step 1: Scan Blockers
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute scan blockers operations for the Cross Team Dependency Tracker workflow.
Expected: `scan_blockers_artifacts`

### Step 2: Trace Dependencies [depends_on: scan_blockers]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute trace dependencies operations for the Cross Team Dependency Tracker workflow.
Expected: `trace_dependencies_artifacts`

### Step 3: Escalation Report [depends_on: trace_dependencies]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute escalation report operations for the Cross Team Dependency Tracker workflow.
Expected: `escalation_report_artifacts`

### Step 4: KG Persistence [depends_on: escalation_report]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Cross Team Dependency Tracker results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Scan Blockers
- **After level 0:** Step 2 — Trace Dependencies
- **After level 1:** Step 3 — Escalation Report
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
