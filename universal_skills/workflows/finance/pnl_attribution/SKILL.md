---
name: pnl_attribution
description: >-
  Parallel execution workflow for pnl attribution using the Unified Parallel Engine
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
tags: [finance, pnl-attribution]
concept: CONCEPT:EE-011
---

# Pnl Attribution Workflow

**CONCEPT:EE-011**

Parallel execution workflow for pnl attribution using the Unified Parallel Engine

## Steps

### Step 1: Fetch Trades
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute fetch trades operations for the Pnl Attribution workflow.
Expected: `fetch_trades_artifacts`

### Step 2: Decompose By Strategy [depends_on: fetch_trades]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute decompose by strategy operations for the Pnl Attribution workflow.
Expected: `decompose_by_strategy_artifacts`

### Step 3: Alpha Vs Beta [depends_on: decompose_by_strategy]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute alpha vs beta operations for the Pnl Attribution workflow.
Expected: `alpha_vs_beta_artifacts`

### Step 4: Report [depends_on: alpha_vs_beta]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute report operations for the Pnl Attribution workflow.
Expected: `report_artifacts`

### Step 5: KG Persistence [depends_on: report]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Pnl Attribution results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
