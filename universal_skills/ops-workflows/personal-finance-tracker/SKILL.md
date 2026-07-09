---
name: personal-finance-tracker
skill_type: workflow
description: >-
  Parallel execution workflow for personal finance tracker using the Unified Parallel Engine
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
tags: [ops, personal-finance-tracker]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.0.2'
---

# Personal Finance Tracker Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for personal finance tracker using the Unified Parallel Engine

## Steps

### Step 1: Collect Transactions
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute collect transactions operations for the Personal Finance Tracker workflow.
Expected: `collect_transactions_artifacts`

### Step 2: Categorize [depends_on: collect_transactions]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute categorize operations for the Personal Finance Tracker workflow.
Expected: `categorize_artifacts`

### Step 3: Budget Comparison [depends_on: categorize]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute budget comparison operations for the Personal Finance Tracker workflow.
Expected: `budget_comparison_artifacts`

### Step 4: Report [depends_on: budget_comparison]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute report operations for the Personal Finance Tracker workflow.
Expected: `report_artifacts`

### Step 5: KG Persistence [depends_on: report]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Personal Finance Tracker results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Collect Transactions
- **After level 0:** Step 2 — Categorize
- **After level 1:** Step 3 — Budget Comparison
- **After level 2:** Step 4 — Report
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
