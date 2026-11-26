---
name: strategy-tournament
skill_type: workflow
description: >-
  Performs concurrent backtests across 10 distinct algorithmic strategies, evaluates risk-adjusted metrics, ranks return profiles, and selects the top models.
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
tags: [tournament, evaluation, metrics, selection]
concept: CONCEPT:EE-011
metadata:
  version: '1.6.2'
---

# Strategy Tournament Workflow

**CONCEPT:EE-011**

Performs concurrent backtests across 10 distinct algorithmic strategies, evaluates risk-adjusted metrics, ranks return profiles, and selects the top models.

## Steps

1. Run concurrent backtests for the candidate strategies with `graph_query` and `sx_search`. Verify that `batch-backtest-outputs` has one result per strategy.
2. Compute Sharpe, Sortino, Calmar and max drawdown with `graph_analyze`. Verify that `strategy-performance-scorecards` has all four metrics per strategy.
3. Rank and select the top models with `graph_query` and `graph_analyze`. Verify that `winning-strategies-selection` lists exactly the top 3.
4. Compile the tearsheet with `graph_write` and `document_tools`. Verify that `tournament-summary-report` is produced.
5. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

### Step 1: Backtest Batch Runner
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Runs historical backtests concurrently for 10 distinct trading strategies.
Expected: `batch-backtest-outputs`

### Step 2: Metric Evaluator [depends_on: backtest-batch-runner]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Computes Sharpe, Sortino, Calmar ratios, and max drawdown for each candidate.
Expected: `strategy-performance-scorecards`

### Step 3: Ranker Selector [depends_on: metric-evaluator]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Ranks strategies and selects the top 3 best-performing models.
Expected: `winning-strategies-selection`

### Step 4: Synthesis Compiler [depends_on: ranker-selector]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Synthesizes results into a unified strategic tearsheet.
Expected: `tournament-summary-report`

### Step 5: KG Persistence [depends_on: synthesis-compiler]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| A backtest is missing from the batch | Strategy failed to run | Check its error in the batch output, fix it, and re-run only that strategy. |
| Metrics are NaN | Zero-variance or too-short return series | Extend the backtest window and recompute with `graph_analyze`. |
| Ranking is a tie | Equal Sharpe values | Break ties by max drawdown and record the rule in the report. |

## Output
- Strategy Tournament results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Backtest Batch Runner
- **After level 0:** Step 2 — Metric Evaluator
- **After level 1:** Step 3 — Ranker Selector
- **After level 2:** Step 4 — Synthesis Compiler
- **After level 3:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
