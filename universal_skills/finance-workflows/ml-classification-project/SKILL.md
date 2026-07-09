---
name: ml-classification-project
skill_type: workflow
description: >-
  Build the ML-classification portfolio project: engineer technical-indicator
  features, train an XGBoost model to predict whether the S&P 500 will be up or
  down tomorrow, benchmark it against a coin flip, and publish a GitHub repo.
domain: finance-workflows
agent: quant_researcher
team_config: quantitative_trading_team
tags: [quant, machine-learning, xgboost, classification, portfolio, workflow]
metadata:
  version: '1.0.2'
  author: agent-utilities
  concept: 'CONCEPT:KG-2.6'
---

# ML Classification Project Workflow

Project 5 of the quant portfolio. Predict next-day direction (not price) and
benchmark honestly against a coin flip. See
`quant-career-docs/reference/ml-for-finance.md`.

## Steps

### Step 1: engineer-features
**Agent**: `quant_researcher`
**Tools**: `data-science-mcp`

Pull S&P 500 history via yfinance and engineer technical-indicator features
(returns, moving averages, RSI, volatility, momentum). Ensure features use only
past data — no lookahead.
Expected: `feature-matrix`

### Step 2: train-xgboost [depends_on: Step 1]
**Agent**: `quant_researcher`

Train an XGBoost/LightGBM classifier to predict up/down for the next day. Use
time-aware train/test splitting (no shuffling across time).
Expected: `trained-classifier`

### Step 3: benchmark-coinflip [depends_on: Step 2]
**Agent**: `quant_researcher`

Evaluate out-of-sample accuracy/AUC and benchmark against a 50/50 coin flip and a
naive majority-class baseline.
Expected: `benchmark-comparison`

### Step 4: evaluate [depends_on: Step 3]
**Agent**: `risk_analyst`

If the classifier drives a strategy, report Sharpe, max drawdown, CAGR vs
benchmark. State whether the edge survives costs — honest analysis.
Expected: `evaluation-metrics`

### Step 5: github-publish [depends_on: Step 4]
**Agent**: `quant_developer`

Publish a GitHub repo with README, metrics, the coin-flip benchmark, clean code,
and an honest "what didn't work" section.
Expected: `github-repo-url`

### Step 6: kg-persist [depends_on: Step 5]
**Agent**: `quant_researcher`
**Tools**: `graph_write`

Persist the project and metrics as typed nodes linked to the portfolio.

## Output
- An XGBoost direction classifier benchmarked against a coin flip
- A published GitHub portfolio repo

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — engineer-features
- **After level 0:** Step 2 — train-xgboost
- **After level 1:** Step 3 — benchmark-coinflip
- **After level 2:** Step 4 — evaluate
- **After level 3:** Step 5 — github-publish
- **After level 4:** Step 6 — kg-persist

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
