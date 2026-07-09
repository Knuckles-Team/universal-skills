---
name: overnight_research_loop
description: >-
  Runs overnight crawling of news/publications to generate factor hypotheses, runs backtests in parallel, debates findings, and generates a morning briefing.
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
tags: [overnight, research, backtest, factor]
concept: CONCEPT:EE-011
---

# Overnight Research Loop Workflow

**CONCEPT:EE-011**

Runs overnight crawling of news/publications to generate factor hypotheses, runs backtests in parallel, debates findings, and generates a morning briefing.

## Steps

### Step 1: Hypothesis Crawlers
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Scans academic publications, social feeds, and market tickers overnight to find potential factor ideas.
Expected: `factor-hypothesis-list`

### Step 2: Parallel Backtester [depends_on: hypothesis-crawlers]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Runs backtests concurrently across 50 parameter configurations.
Expected: `multi-config-backtest-results`

### Step 3: Factor Debater [depends_on: parallel-backtester]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Analyzes return profile, drawdown, and transaction cost impact in a swarm debate.
Expected: `approved-factor-signals`

### Step 4: Report Compiler [depends_on: factor-debater]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Compiles findings into a formatted dashboard report for the morning review.
Expected: `morning-research-tearsheet`

### Step 5: KG Persistence [depends_on: report-compiler]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Overnight Research Loop results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Hypothesis Crawlers
- **After level 0:** Step 2 — Parallel Backtester
- **After level 1:** Step 3 — Factor Debater
- **After level 2:** Step 4 — Report Compiler
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
