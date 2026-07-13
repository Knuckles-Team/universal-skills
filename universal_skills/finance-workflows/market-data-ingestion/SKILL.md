---
name: market-data-ingestion
skill_type: workflow
description: >-
  Parallel execution workflow for market data ingestion using the Unified Parallel Engine
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
tags: [finance, market-data-ingestion]
concept: CONCEPT:EE-011
metadata:
  version: '1.2.1'
---

# Market Data Ingestion Workflow

**CONCEPT:EE-011**

Parallel execution workflow for market data ingestion using the Unified Parallel Engine

## Steps

### Step 1: Exchange
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute exchange operations for the Market Data Ingestion workflow.
Expected: `exchange_artifacts`

### Step 2: News
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute news operations for the Market Data Ingestion workflow.
Expected: `news_artifacts`

### Step 3: Alternative Data
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute alternative data operations for the Market Data Ingestion workflow.
Expected: `alternative_data_artifacts`

### Step 4: Normalize [depends_on: exchange, news, alternative_data]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute normalize operations for the Market Data Ingestion workflow.
Expected: `normalize_artifacts`

### Step 5: Store [depends_on: normalize]
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute store operations for the Market Data Ingestion workflow.
Expected: `store_artifacts`

### Step 6: KG Persistence [depends_on: store]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Market Data Ingestion results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Exchange; Step 2 — News; Step 3 — Alternative Data
- **After level 0:** Step 4 — Normalize
- **After level 1:** Step 5 — Store
- **After level 2:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
