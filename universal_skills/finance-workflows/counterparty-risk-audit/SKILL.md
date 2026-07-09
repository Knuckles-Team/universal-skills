---
name: counterparty-risk-audit
skill_type: workflow
description: >-
  Parallel execution workflow for counterparty risk audit using the Unified Parallel Engine
domain: finance-workflows
agent: quant_analyst
team_config:
  name: quantitative_trading_team
  task_pattern: quantitative analysis and financial computation
  execution_mode: parallel
  specialist_ids:
    - data-fetcher
    - compute-engine
    - risk-assessor
    - report-generator
  tool_assignments:
    data-fetcher: [graph_query, sx_search]
    compute-engine: [graph_analyze]
    risk-assessor: [graph_query, graph_analyze]
    report-generator: [graph_write, document_tools]
tags: [finance, counterparty-risk-audit]
concept: CONCEPT:EE-011
metadata:
  version: '1.0.2'
---

# Counterparty Risk Audit Workflow

**CONCEPT:EE-011**

Parallel execution workflow for counterparty risk audit using the Unified Parallel Engine

## Steps

### Step 1: Volume
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute volume operations for the Counterparty Risk Audit workflow.
Expected: `volume_artifacts`

### Step 2: Insurance Fund
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute insurance fund operations for the Counterparty Risk Audit workflow.
Expected: `insurance_fund_artifacts`

### Step 3: Withdrawal Test
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute withdrawal test operations for the Counterparty Risk Audit workflow.
Expected: `withdrawal_test_artifacts`

### Step 4: Score [depends_on: volume, insurance_fund, withdrawal_test]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute score operations for the Counterparty Risk Audit workflow.
Expected: `score_artifacts`

### Step 5: KG Persistence [depends_on: score]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Counterparty Risk Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Volume; Step 2 — Insurance Fund; Step 3 — Withdrawal Test
- **After level 0:** Step 4 — Score
- **After level 1:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
