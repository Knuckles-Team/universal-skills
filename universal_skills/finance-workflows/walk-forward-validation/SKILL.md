---
name: walk-forward-validation
description: >-
  Divides historical feeds into overlapping walk-forward segments, runs parallel window fits, tests out-of-sample stability, and aggregates validation statistics.
domain: finance
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
tags: [walk-forward, validation, oversitting, backtest]
concept: CONCEPT:EE-011
---

# Walk Forward Validation Workflow

**CONCEPT:EE-011**

Divides historical feeds into overlapping walk-forward segments, runs parallel window fits, tests out-of-sample stability, and aggregates validation statistics.

## Steps

### Step 1: Window Generator
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Divides historical market data into 5 overlapping training and testing segments.
Expected: `segmented-walk-forward-windows`

### Step 2: Model Train Batch [depends_on: window-generator]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Runs parallel training sessions across all segmented windows.
Expected: `window-fit-parameters`

### Step 3: Out Of Sample Test [depends_on: model-train-batch]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Backtests the fitted parameters on the subsequent test segments.
Expected: `out-of-sample-performances`

### Step 4: Aggregate Validator [depends_on: out-of-sample-test]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Combines out-of-sample returns to verify strategy stability.
Expected: `final-walk-forward-report`

### Step 5: KG Persistence [depends_on: aggregate-validator]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Walk Forward Validation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Window Generator
- **After level 0:** Step 2 — Model Train Batch
- **After level 1:** Step 3 — Out Of Sample Test
- **After level 2:** Step 4 — Aggregate Validator
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
