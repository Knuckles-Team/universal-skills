---
name: strategy_hypothesis_to_live
description: Formulates new trading strategies, runs a swarm debate to vet them, backtests them, and rolls out from paper trade to live capital endpoints.
domain: finance
tags: [lifecycle, backtest, debate, live]
---
# Strategy Hypothesis To Live Workflow

This workflow coordinates multi-agent parallel executions of Formulates new trading strategies, runs a swarm debate to vet them, backtests them, and rolls out from paper trade to live capital endpoints.

### Step 1: hypothesis-generator [depends_on: none]
Formulates new trading strategies using historical market regimes and anomalies data.
Expected: strategy-blueprint

### Step 2: swarm-debate [depends_on: hypothesis-generator]
Runs a quant debate between analyst and trader to vet the strategy logic.
Expected: debate-transcript-and-feedback

### Step 3: backtest-evaluator [depends_on: swarm-debate]
Backtests the strategy over 5 years of historical tick-level data.
Expected: backtest-performance-metrics

### Step 4: paper-trade-run [depends_on: backtest-evaluator]
Deploys to a simulated paper trading exchange for 30 days to measure forward performance.
Expected: paper-trade-forward-tearsheet

### Step 5: live-deploy-gate [depends_on: paper-trade-run]
Formally deploys the strategy to live execution with restricted capital limits.
Expected: live-deployment-receipt

