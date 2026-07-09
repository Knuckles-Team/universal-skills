---
name: sentiment-alpha-project
skill_type: workflow
description: >-
  Build the sentiment-alpha portfolio project: scrape financial news headlines
  (NewsAPI free tier), score them with FinBERT, construct a sentiment signal,
  backtest it leak-free, and publish a GitHub repo.
domain: finance-workflows
agent: quant_researcher
team_config: quantitative_trading_team
tags: [quant, sentiment, finbert, nlp, alpha, portfolio, workflow]
metadata:
  version: '1.1.0'
  author: agent-utilities
  concept: 'CONCEPT:KG-2.6'
---

# Sentiment Alpha Project Workflow

Project 4 of the quant portfolio. Turn news sentiment into a tradable signal. See
`quant-career-docs/reference/ml-for-finance.md`.

## Steps

### Step 1: scrape-news
**Agent**: `quant_developer`
**Tools**: `data-science-mcp`

Pull financial news headlines for target tickers from the NewsAPI free tier.
Timestamp each headline for point-in-time alignment (avoid lookahead).
Expected: `timestamped-headlines`

### Step 2: finbert-score [depends_on: Step 1]
**Agent**: `quant_researcher`

Run FinBERT over the headlines to produce per-headline sentiment scores
(positive/negative/neutral).
Expected: `sentiment-scores`

### Step 3: build-signal [depends_on: Step 2]
**Agent**: `quant_researcher`

Aggregate sentiment into a daily per-ticker signal; define the mapping from
sentiment to position (long/flat/short).
Expected: `sentiment-signal`

### Step 4: backtest [depends_on: Step 3]
**Agent**: `quant_developer`

Backtest the sentiment signal with realistic fees/slippage; audit for lookahead
bias. Report Sharpe, max drawdown, CAGR vs benchmark.
Expected: `backtest-metrics`

### Step 5: github-publish [depends_on: Step 4]
**Agent**: `quant_developer`

Publish a GitHub repo with README, metrics, clean code, and an honest "what didn't
work" section.
Expected: `github-repo-url`

### Step 6: kg-persist [depends_on: Step 5]
**Agent**: `quant_researcher`
**Tools**: `graph_write`

Persist the project and metrics as typed nodes linked to the portfolio.

## Output
- A FinBERT-driven sentiment-alpha signal, backtested honestly
- A published GitHub portfolio repo

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — scrape-news
- **After level 0:** Step 2 — finbert-score
- **After level 1:** Step 3 — build-signal
- **After level 2:** Step 4 — backtest
- **After level 3:** Step 5 — github-publish
- **After level 4:** Step 6 — kg-persist

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
