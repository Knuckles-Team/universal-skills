---
name: volatility_forecast_project
description: >-
  Build the volatility-forecasting portfolio project: fit GARCH models to forecast
  daily volatility, compare the forecast against realized volatility, evaluate the
  fit, and publish a GitHub repo. This is literally what risk desks do.
domain: finance
agent: risk_analyst
team_config: trading_department
tags: [quant, volatility, garch, risk, forecasting, portfolio, workflow]
metadata:
  author: agent-utilities
  version: '1.0.0'
  concept: 'CONCEPT:KG-2.6'
---

# Volatility Forecasting Project Workflow

Project 3 of the quant portfolio. Forecast daily volatility with GARCH and grade
it against realized vol. See `quant-career-docs/reference/ml-for-finance.md` and
the Risk Analyst persona.

## Steps

### Step 1: fetch-price-data
**Agent**: `quant_developer`
**Tools**: `data-science-mcp`

Pull historical prices via yfinance and compute daily returns.
Expected: `daily-returns`

### Step 2: fit-garch [depends_on: Step 1]
**Agent**: `risk_analyst`

Fit a GARCH(1,1) (or variant) model to the return series using the `arch` library.
Capture conditional-volatility estimates.
Expected: `garch-volatility-forecast`

### Step 3: forecast-vs-realized [depends_on: Step 2]
**Agent**: `risk_analyst`

Produce out-of-sample volatility forecasts and align them against realized
volatility (e.g. rolling standard deviation of returns).
Expected: `forecast-realized-pairs`

### Step 4: evaluate [depends_on: Step 3]
**Agent**: `risk_analyst`

Evaluate forecast accuracy (e.g. RMSE, QLIKE). State where the model under- or
over-predicts — honest analysis.
Expected: `forecast-evaluation`

### Step 5: github-publish [depends_on: Step 4]
**Agent**: `quant_developer`

Publish a GitHub repo with README, forecast-vs-realized plots, evaluation metrics,
clean code, and an honest "what didn't work" section.
Expected: `github-repo-url`

### Step 6: kg-persist [depends_on: Step 5]
**Agent**: `risk_analyst`
**Tools**: `graph_write`

Persist the project and evaluation metrics as typed nodes linked to the portfolio.

## Output
- A GARCH volatility forecaster graded against realized vol
- A published GitHub portfolio repo

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — fetch-price-data
- **After level 0:** Step 2 — fit-garch
- **After level 1:** Step 3 — forecast-vs-realized
- **After level 2:** Step 4 — evaluate
- **After level 3:** Step 5 — github-publish
- **After level 4:** Step 6 — kg-persist

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
