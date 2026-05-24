---
name: strategy_tournament
description: Performs concurrent backtests across 10 distinct algorithmic strategies, evaluates risk-adjusted metrics, ranks return profiles, and selects the top models.
domain: finance
tags: [tournament, evaluation, metrics, selection]
---
# Strategy Tournament Workflow

This workflow coordinates multi-agent parallel executions of Performs concurrent backtests across 10 distinct algorithmic strategies, evaluates risk-adjusted metrics, ranks return profiles, and selects the top models.

### Step 1: backtest-batch-runner [depends_on: none]
Runs historical backtests concurrently for 10 distinct trading strategies.
Expected: batch-backtest-outputs

### Step 2: metric-evaluator [depends_on: backtest-batch-runner]
Computes Sharpe, Sortino, Calmar ratios, and max drawdown for each candidate.
Expected: strategy-performance-scorecards

### Step 3: ranker-selector [depends_on: metric-evaluator]
Ranks strategies and selects the top 3 best-performing models.
Expected: winning-strategies-selection

### Step 4: synthesis-compiler [depends_on: ranker-selector]
Synthesizes results into a unified strategic tearsheet.
Expected: tournament-summary-report

