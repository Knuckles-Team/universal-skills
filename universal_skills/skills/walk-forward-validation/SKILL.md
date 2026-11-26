---
name: walk-forward-validation
skill_type: workflow
description: >-
  Divides historical feeds into overlapping walk-forward segments, runs parallel window fits, tests out-of-sample stability, and aggregates validation statistics.
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
tags: [walk-forward, validation, oversitting, backtest]
concept: CONCEPT:EE-011
metadata:
  version: '1.6.2'
---

# Walk Forward Validation Workflow

**CONCEPT:EE-011**

Divides historical feeds into overlapping walk-forward segments, runs parallel window fits, tests out-of-sample stability, and aggregates validation statistics.

## Steps

1. Generate 5 overlapping train and test windows with `graph_query` and `sx_search`. Verify that `segmented-walk-forward-windows` has 5 windows with non-overlapping test periods.
2. Train a model per window with `graph_analyze`. Verify that `window-fit-parameters` has one entry per window.
3. Backtest each fit on its test segment with `graph_query` and `graph_analyze`. Verify that `out-of-sample-performances` has a result per window.
4. Aggregate out-of-sample returns with `graph_write` and `document_tools`. Verify that `final-walk-forward-report` shows stability across windows.
5. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

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

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Windows leak future data | Test period overlaps training | Regenerate windows so each test starts after its training end. |
| A window fit fails | Too little data in that window | Lengthen the training window or reduce the window count, and rerun that fit. |
| Performance varies widely | Strategy is unstable | Report the instability and do not promote the strategy. |

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

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
