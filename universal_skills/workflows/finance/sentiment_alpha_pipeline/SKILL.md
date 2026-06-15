---
name: sentiment_alpha_pipeline
description: >-
  Crawls web news, evaluates social posts sentiment spikes, fuses sentiment signals, and backtests correlation results.
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
tags: [sentiment, crawler, social, nlp]
concept: CONCEPT:EE-011
---

# Sentiment Alpha Pipeline Workflow

**CONCEPT:EE-011**

Crawls web news, evaluates social posts sentiment spikes, fuses sentiment signals, and backtests correlation results.

## Steps

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

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
