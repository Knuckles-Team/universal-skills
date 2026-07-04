---
name: sla_compliance_monitor
description: >-
  Parallel execution workflow for sla compliance monitor using the Unified Parallel Engine
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
tags: [ops, sla-compliance-monitor]
concept: CONCEPT:KG-2.12
---

# Sla Compliance Monitor Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for sla compliance monitor using the Unified Parallel Engine

## Steps

### Step 1: Check Response Times
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute check response times operations for the Sla Compliance Monitor workflow.
Expected: `check_response_times_artifacts`

### Step 2: Resolution Times [depends_on: check_response_times]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute resolution times operations for the Sla Compliance Monitor workflow.
Expected: `resolution_times_artifacts`

### Step 3: Breach Alerts [depends_on: resolution_times]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute breach alerts operations for the Sla Compliance Monitor workflow.
Expected: `breach_alerts_artifacts`

### Step 4: KG Persistence [depends_on: breach_alerts]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Sla Compliance Monitor results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Check Response Times
- **After level 0:** Step 2 — Resolution Times
- **After level 1:** Step 3 — Breach Alerts
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
