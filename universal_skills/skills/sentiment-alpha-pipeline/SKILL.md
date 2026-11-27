---
name: sentiment-alpha-pipeline
skill_type: workflow
description: >-
  Crawls web news, evaluates social posts sentiment spikes, fuses sentiment signals, and backtests correlation results.
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
tags: [sentiment, crawler, social, nlp]
concept: CONCEPT:EE-011
metadata:
  version: '1.7.0'
---

# Sentiment Alpha Pipeline Workflow

**CONCEPT:EE-011**

Crawls web news, evaluates social posts sentiment spikes, fuses sentiment signals, and backtests correlation results.

## Steps

1. Scrape recent news, blogs and academic articles with `graph_query` and `sx_search`. Verify that `raw-news-and-publications-logs` has timestamps for each item.
2. Monitor social platforms for ticker sentiment spikes with `graph_analyze`. Verify that `raw-social-mentions-counts` has counts per ticker and time bucket.
3. Fuse the news and social signals into one sentiment score with `graph_query` and `graph_analyze`. Verify that `fused-sentiment-signals` covers each ticker present in both inputs.
4. Backtest the fused signal on history with `graph_write` and `document_tools`. Verify that `sentiment-backtest-metrics` reports Sharpe and drawdown.
5. Persist the results as typed nodes and edges with `graph_write`. Verify that a follow-up `graph_query` returns the new nodes linked to existing domain entities.

### Step 1: Web News Scraper
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Scrapes recent news feeds, financial blogs, and academic search articles.
Expected: `raw-news-and-publications-logs`

### Step 2: Social Sentiment Analyzer
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Monitors social platforms for ticker sentiment spikes.
Expected: `raw-social-mentions-counts`

### Step 3: Signal Score Fuser [depends_on: web-news-scraper, social-sentiment-analyzer]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Combines news and social signals into a unified sentiment score.
Expected: `fused-sentiment-signals`

### Step 4: Backtest Verifier [depends_on: signal-score-fuser]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Tests the sentiment signal returns profile in historical backtests.
Expected: `sentiment-backtest-metrics`

### Step 5: KG Persistence [depends_on: backtest-verifier]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| News scrape returns nothing | The feeds are blocked or the tickers are misspelled | Fix the tickers and query another source with `sx_search`. |
| Fused signal is empty | News and social inputs share no tickers or timestamps | Align the time buckets of both inputs and re-run the fusion with `graph_analyze`. |
| `graph_write` persistence is rejected | A node has no type or no link target | Re-issue `graph_write` with a typed node and an edge to an entity located first with `graph_query`. |
| `graph_orchestrate` cannot run the DAG | arbora is unreachable | Skip the offload and execute the steps natively in dependency order as described under `## Execution`. |

## Output
- Sentiment Alpha Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Web News Scraper; Step 2 — Social Sentiment Analyzer
- **After level 0:** Step 3 — Signal Score Fuser
- **After level 1:** Step 4 — Backtest Verifier
- **After level 2:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
