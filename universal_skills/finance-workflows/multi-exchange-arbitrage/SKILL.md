---
name: multi-exchange-arbitrage
skill_type: workflow
description: >-
  Scans feeds across spot and derivative exchanges concurrently, computes fee-adjusted spread funding margins, and executes both legs.
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
tags: [arbitrage, multi-exchange, derivatives, spot]
concept: CONCEPT:EE-011
metadata:
  version: '1.2.0'
---

# Multi Exchange Arbitrage Workflow

**CONCEPT:EE-011**

Scans feeds across spot and derivative exchanges concurrently, computes fee-adjusted spread funding margins, and executes both legs.

## Steps

### Step 1: Ticker Scanner
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Pull price feeds across multiple spot and derivative exchange endpoints concurrently.
Expected: `real-time-ticker-feeds`

### Step 2: Spread Analyzer [depends_on: ticker-scanner]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Calculate transaction-fee adjusted funding and spot-futures spreads in real time.
Expected: `arbitrage-spread-metrics`

### Step 3: Order Executor [depends_on: spread-analyzer]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Simultaneously routes buy and sell legs to the respective exchanges.
Expected: `order-execution-status`

### Step 4: Pnl Settler [depends_on: order-executor]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Audits trade fills, records ledger transaction records, and calculates net PnL.
Expected: `settlement-ledger-entries`

### Step 5: KG Persistence [depends_on: pnl-settler]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Multi Exchange Arbitrage results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Ticker Scanner
- **After level 0:** Step 2 — Spread Analyzer
- **After level 1:** Step 3 — Order Executor
- **After level 2:** Step 4 — Pnl Settler
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
