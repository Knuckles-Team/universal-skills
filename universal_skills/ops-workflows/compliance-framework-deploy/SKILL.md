---
name: compliance-framework-deploy
description: >-
  Parallel execution workflow for compliance framework deploy using the Unified Parallel Engine
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
tags: [ops, compliance-framework-deploy]
concept: CONCEPT:KG-2.12
---

# Compliance Framework Deploy Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for compliance framework deploy using the Unified Parallel Engine

## Steps

### Step 1: Select Framework
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute select framework operations for the Compliance Framework Deploy workflow.
Expected: `select_framework_artifacts`

### Step 2: Gap Analysis [depends_on: select_framework]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute gap analysis operations for the Compliance Framework Deploy workflow.
Expected: `gap_analysis_artifacts`

### Step 3: Parallel Impl Per Control [depends_on: gap_analysis]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute parallel impl per control operations for the Compliance Framework Deploy workflow.
Expected: `parallel_impl_per_control_artifacts`

### Step 4: Audit [depends_on: parallel_impl_per_control]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute audit operations for the Compliance Framework Deploy workflow.
Expected: `audit_artifacts`

### Step 5: KG Persistence [depends_on: audit]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Compliance Framework Deploy results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Select Framework
- **After level 0:** Step 2 — Gap Analysis
- **After level 1:** Step 3 — Parallel Impl Per Control
- **After level 2:** Step 4 — Audit
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
