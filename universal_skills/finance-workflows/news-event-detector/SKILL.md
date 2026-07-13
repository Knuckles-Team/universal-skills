---
name: news-event-detector
skill_type: workflow
description: >-
  Parallel execution workflow for news event detector using the Unified Parallel Engine
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
tags: [finance, news-event-detector]
concept: CONCEPT:EE-011
metadata:
  version: '1.2.1'
---

# News Event Detector Workflow

**CONCEPT:EE-011**

Parallel execution workflow for news event detector using the Unified Parallel Engine

## Steps

### Step 1: Rss
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute rss operations for the News Event Detector workflow.
Expected: `rss_artifacts`

### Step 2: Twitter
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute twitter operations for the News Event Detector workflow.
Expected: `twitter_artifacts`

### Step 3: Reddit
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute reddit operations for the News Event Detector workflow.
Expected: `reddit_artifacts`

### Step 4: News Apis
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute news apis operations for the News Event Detector workflow.
Expected: `news_apis_artifacts`

### Step 5: Classify [depends_on: rss, twitter, reddit, news_apis]
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute classify operations for the News Event Detector workflow.
Expected: `classify_artifacts`

### Step 6: Trade Signal [depends_on: classify]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute trade signal operations for the News Event Detector workflow.
Expected: `trade_signal_artifacts`

### Step 7: KG Persistence [depends_on: trade_signal]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- News Event Detector results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Rss; Step 2 — Twitter; Step 3 — Reddit; Step 4 — News Apis
- **After level 0:** Step 5 — Classify
- **After level 1:** Step 6 — Trade Signal
- **After level 2:** Step 7 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
