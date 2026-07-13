---
name: factor-model-project
skill_type: workflow
description: >-
  Build the Fama-French 3-factor portfolio project: download the free factor data
  from Kenneth French's website, regress a portfolio's returns against market,
  size, and value factors, interpret the loadings, and publish a GitHub repo.
domain: finance-workflows
agent: quant_researcher
team_config: quantitative_trading_team
tags: [quant, factor-model, fama-french, regression, portfolio, workflow]
metadata:
  version: '1.2.1'
  author: agent-utilities
  concept: 'CONCEPT:KG-2.6'
---

# Factor Model Project Workflow

Project 2 of the quant portfolio. Replicate the Fama-French 3-factor model (market
beta, size, value). See `quant-career-docs/reference/strategies.md`.

## Steps

### Step 1: fetch-french-factors
**Agent**: `quant_researcher`
**Tools**: `data-science-mcp`

Download the Fama-French 3-factor data (Mkt-RF, SMB, HML, RF) from Kenneth
French's website. Align the date index.
Expected: `factor-returns`

### Step 2: fetch-returns
**Agent**: `quant_developer`
**Tools**: `data-science-mcp`

Pull returns for a portfolio or asset under study via yfinance; compute excess
returns over the risk-free rate.
Expected: `excess-returns`

### Step 3: regress-factors [depends_on: Step 1, Step 2]
**Agent**: `quant_researcher`

Regress excess returns on the three factors (OLS via statsmodels). Capture
coefficients, t-stats, and R-squared.
Expected: `factor-loadings`

### Step 4: interpret-loadings [depends_on: Step 3]
**Agent**: `quant_researcher`

Interpret the loadings (market/size/value tilt) and alpha. State what the model
does and does not explain — honest analysis.
Expected: `factor-interpretation`

### Step 5: github-publish [depends_on: Step 4]
**Agent**: `quant_developer`

Publish a GitHub repo with README, regression results, clean code, and an honest
"what didn't work" section.
Expected: `github-repo-url`

### Step 6: kg-persist [depends_on: Step 5]
**Agent**: `quant_researcher`
**Tools**: `graph_write`

Persist the project and factor loadings as typed nodes linked to the portfolio.

## Output
- A reproduced Fama-French 3-factor regression with interpreted loadings
- A published GitHub portfolio repo

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — fetch-french-factors; Step 2 — fetch-returns
- **After level 0:** Step 3 — regress-factors
- **After level 1:** Step 4 — interpret-loadings
- **After level 2:** Step 5 — github-publish
- **After level 3:** Step 6 — kg-persist

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
