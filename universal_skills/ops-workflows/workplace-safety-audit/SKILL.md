---
name: workplace-safety-audit
description: >-
  Parallel execution workflow for workplace safety audit using the Unified Parallel Engine
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
tags: [ops, workplace-safety-audit]
concept: CONCEPT:KG-2.12
---

# Workplace Safety Audit Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for workplace safety audit using the Unified Parallel Engine

## Steps

### Step 1: Checklist
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute checklist operations for the Workplace Safety Audit workflow.
Expected: `checklist_artifacts`

### Step 2: Findings [depends_on: checklist]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute findings operations for the Workplace Safety Audit workflow.
Expected: `findings_artifacts`

### Step 3: Remediation Plan [depends_on: findings]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute remediation plan operations for the Workplace Safety Audit workflow.
Expected: `remediation_plan_artifacts`

### Step 4: Follow Up [depends_on: remediation_plan]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute follow up operations for the Workplace Safety Audit workflow.
Expected: `follow_up_artifacts`

### Step 5: KG Persistence [depends_on: follow_up]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Workplace Safety Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Checklist
- **After level 0:** Step 2 — Findings
- **After level 1:** Step 3 — Remediation Plan
- **After level 2:** Step 4 — Follow Up
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
