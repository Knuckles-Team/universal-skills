---
name: quarterly-business-review
skill_type: workflow
description: >-
  Parallel execution workflow for quarterly business review using the Unified Parallel Engine
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
tags: [ops, quarterly-business-review]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.2.0'
---

# Quarterly Business Review Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for quarterly business review using the Unified Parallel Engine

## Steps

### Step 1: Financial
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute financial operations for the Quarterly Business Review workflow.
Expected: `financial_artifacts`

### Step 2: Operational
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute operational operations for the Quarterly Business Review workflow.
Expected: `operational_artifacts`

### Step 3: Customer
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute customer operations for the Quarterly Business Review workflow.
Expected: `customer_artifacts`

### Step 4: Product Metrics
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute product metrics operations for the Quarterly Business Review workflow.
Expected: `product_metrics_artifacts`

### Step 5: Presentation [depends_on: financial, operational, customer, product_metrics]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute presentation operations for the Quarterly Business Review workflow.
Expected: `presentation_artifacts`

### Step 6: KG Persistence [depends_on: presentation]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Quarterly Business Review results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Financial; Step 2 — Operational; Step 3 — Customer; Step 4 — Product Metrics
- **After level 0:** Step 5 — Presentation
- **After level 1:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
