---
name: pnl-attribution
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

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fetch Trades
- **After level 0:** Step 2 — Decompose By Strategy
- **After level 1:** Step 3 — Alpha Vs Beta
- **After level 2:** Step 4 — Report
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
