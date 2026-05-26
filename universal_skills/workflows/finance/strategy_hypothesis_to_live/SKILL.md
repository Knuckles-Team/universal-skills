---
name: strategy_hypothesis_to_live
description: >-
  Formulates new trading strategies, runs a swarm debate to vet them, backtests them, and rolls out from paper trade to live capital endpoints.
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
tags: [lifecycle, backtest, debate, live]
concept: CONCEPT:EE-011
---

# Strategy Hypothesis To Live Workflow

**CONCEPT:EE-011**

Formulates new trading strategies, runs a swarm debate to vet them, backtests them, and rolls out from paper trade to live capital endpoints.

## Steps

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

## Output
- Strategy Hypothesis To Live results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
