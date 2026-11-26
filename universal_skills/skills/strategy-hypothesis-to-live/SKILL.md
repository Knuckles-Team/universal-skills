---
name: strategy-hypothesis-to-live
skill_type: workflow
description: >-
  Formulates new trading strategies, runs a swarm debate to vet them, backtests them, and rolls out from paper trade to live capital endpoints.
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
tags: [lifecycle, backtest, debate, live]
concept: CONCEPT:EE-011
metadata:
  version: '1.6.2'
---

# Strategy Hypothesis To Live Workflow

**CONCEPT:EE-011**

Formulates new trading strategies, runs a swarm debate to vet them, backtests them, and rolls out from paper trade to live capital endpoints.

## Steps

1. Generate hypotheses with `graph_query` and `sx_search` over regimes and anomalies. Verify that `strategy-blueprint` is returned.
2. Vet the logic through the swarm debate with `graph_analyze`. Verify that `debate-transcript-and-feedback` records a verdict.
3. Backtest over the historical window with `graph_query` and `graph_analyze`. Verify that `backtest-performance-metrics` includes return and drawdown.
4. Run the paper-trade period using `graph_write` and `document_tools`. Verify that `paper-trade-forward-tearsheet` covers the full period.
5. Deploy with restricted capital limits only after the paper results pass. Verify that `live-deployment-receipt` shows the capital cap applied.
6. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

### Step 1: Hypothesis Generator
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Formulates new trading strategies using historical market regimes and anomalies data.
Expected: `strategy-blueprint`

### Step 2: Swarm Debate [depends_on: hypothesis-generator]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Runs a quant debate between analyst and trader to vet the strategy logic.
Expected: `debate-transcript-and-feedback`

### Step 3: Backtest Evaluator [depends_on: swarm-debate]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Backtests the strategy over 5 years of historical tick-level data.
Expected: `backtest-performance-metrics`

### Step 4: Paper Trade Run [depends_on: backtest-evaluator]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Deploys to a simulated paper trading exchange for 30 days to measure forward performance.
Expected: `paper-trade-forward-tearsheet`

### Step 5: Live Deploy Gate [depends_on: paper-trade-run]
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Formally deploys the strategy to live execution with restricted capital limits.
Expected: `live-deployment-receipt`

### Step 6: KG Persistence [depends_on: live-deploy-gate]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Debate rejects the strategy | Logic flaws found by the swarm | Revise the blueprint using the feedback and repeat the debate step. |
| Backtest metrics are poor | Overfitting or bad data window | Check the data window and parameters, and re-run the backtest before advancing. |
| Paper trade underperforms backtest | Slippage or regime shift | Do not advance to live. Analyze the tearsheet and return to the hypothesis step. |

## Output
- Strategy Hypothesis To Live results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Hypothesis Generator
- **After level 0:** Step 2 — Swarm Debate
- **After level 1:** Step 3 — Backtest Evaluator
- **After level 2:** Step 4 — Paper Trade Run
- **After level 3:** Step 5 — Live Deploy Gate
- **After level 4:** Step 6 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
