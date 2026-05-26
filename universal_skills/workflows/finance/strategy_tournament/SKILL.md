---
name: strategy_tournament
description: >-
  Performs concurrent backtests across 10 distinct algorithmic strategies, evaluates risk-adjusted metrics, ranks return profiles, and selects the top models.
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
tags: [tournament, evaluation, metrics, selection]
concept: CONCEPT:EE-011
---

# Strategy Tournament Workflow

**CONCEPT:EE-011**

Performs concurrent backtests across 10 distinct algorithmic strategies, evaluates risk-adjusted metrics, ranks return profiles, and selects the top models.

## Steps

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

## Output
- Strategy Tournament results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
