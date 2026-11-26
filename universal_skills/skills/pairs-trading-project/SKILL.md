---
name: pairs-trading-project
skill_type: workflow
description: >-
  Build the pairs-trading portfolio project end-to-end: find two correlated
  stocks, test for cointegration, trade the z-score of their spread, backtest it
  leak-free, report full stats, and publish a GitHub repo. The best single
  learning project in quant finance — teaches hypothesis testing, z-scores,
  position sizing, and risk management at once.
domain: finance-workflows
agent: quant_developer
team_config: quantitative_trading_team
tags: [quant, pairs-trading, cointegration, mean-reversion, portfolio, workflow]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
  concept: 'CONCEPT:KG-2.6'
---

# Pairs Trading Project Workflow

Project 1 of the quant portfolio. Mean reversion on a correlated pair (e.g.
Coca-Cola / Pepsi): when the spread diverges, bet on convergence. See
`quant-career-docs/reference/backtesting.md` and `strategies.md`.

## Steps

1. Fetch two correlated stocks via yfinance with `data-science-mcp`. Verify that `aligned-price-series` shares one index with no forward fill.
2. Run an Engle-Granger test. Verify that `cointegration-pvalue` is below 0.05 before continuing.
3. Compute the rolling z-score and thresholds. Verify that `entry-exit-signals` uses |z|>2 entry and near-0 exit.
4. Backtest in Backtrader or Zipline with fees and slippage. Verify that `backtest-equity-curve` is produced and a lookahead audit is noted.
5. Compute Sharpe, max drawdown and CAGR. Verify that `performance-metrics` identifies failing regimes.
6. Publish with `gh repo create`. Verify that `github-repo-url` loads with the README sections.
7. Persist with `graph_write`. Verify that a `graph_query` returns the project node.

### Step 1: fetch-pair-data
**Agent**: `quant_developer`
**Tools**: `data-science-mcp`

Pull historical price data for two candidate correlated stocks via yfinance. Align
on a common point-in-time index. Avoid any forward-filled future data.
Expected: `aligned-price-series`

### Step 2: cointegration-test [depends_on: Step 1]
**Agent**: `quant_researcher`

Run a cointegration hypothesis test (e.g. Engle-Granger) on the pair. Confirm a
statistically stable long-run spread before proceeding.
Expected: `cointegration-pvalue`

### Step 3: zscore-signal [depends_on: Step 2]
**Agent**: `quant_researcher`

Compute the rolling z-score of the spread. Define entry/exit thresholds (e.g.
enter at |z|>2, exit near 0). Add position sizing and risk limits.
Expected: `entry-exit-signals`

### Step 4: backtest [depends_on: Step 3]
**Agent**: `quant_developer`

Backtest in Backtrader/Zipline with realistic fees and slippage. Audit explicitly
for lookahead bias.
Expected: `backtest-equity-curve`

### Step 5: metrics [depends_on: Step 4]
**Agent**: `risk_analyst`

Compute Sharpe ratio, max drawdown, and CAGR vs benchmark. Identify the regimes
where the strategy fails.
Expected: `performance-metrics`

### Step 6: github-publish [depends_on: Step 5]
**Agent**: `quant_developer`

Publish a GitHub repo: README (what it is + why it should theoretically work),
metrics, clean commented code, and an honest "what didn't work" section.
Expected: `github-repo-url`

### Step 7: kg-persist [depends_on: Step 6]
**Agent**: `quant_developer`
**Tools**: `graph_write`

Persist the project, its metrics, and the repo URL as typed nodes linked to the
quant portfolio in the Knowledge Graph.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| p-value above 0.05 | Pair not cointegrated | Select another candidate pair and restart from the data fetch |
| Sharpe collapses with costs | Overfit | Record the failure in the README's what-didn't-work section and stop rather than tuning on the test set |
| Data misaligned | Different calendars | Reindex both series to the common trading calendar before the cointegration test |

## Output
- A backtested, cointegration-based pairs-trading strategy
- Full performance stats with honest failure analysis
- A published GitHub portfolio repo

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — fetch-pair-data
- **After level 0:** Step 2 — cointegration-test
- **After level 1:** Step 3 — zscore-signal
- **After level 2:** Step 4 — backtest
- **After level 3:** Step 5 — metrics
- **After level 4:** Step 6 — github-publish
- **After level 5:** Step 7 — kg-persist

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
