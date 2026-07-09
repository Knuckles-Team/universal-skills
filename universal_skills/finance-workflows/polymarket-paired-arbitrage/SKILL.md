---
name: polymarket-paired-arbitrage
skill_type: workflow
description: >-
  Scans contract books across Polymarket and other event platforms to identify correlated price anomalies, simulates execution impact, and routes arbitrage trades.
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
tags: [arbitrage, polymarket, execution, simulation]
concept: CONCEPT:EE-011
metadata:
  version: '1.2.0'
---

# Polymarket Paired Arbitrage Workflow

**CONCEPT:EE-011**

Scans contract books across Polymarket and other event platforms to identify correlated price anomalies, simulates execution impact, and routes arbitrage trades.

## Steps

### Step 1: Paired Market Scanner
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Scans contract books across Polymarket and other event platforms to identify correlated price anomalies.
Expected: `arbitrage-opportunities`

### Step 2: Order Book Simulator [depends_on: paired-market-scanner]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Simulates liquidity, bid-ask spreads, and execution impact to verify arbitrage feasibility.
Expected: `simulated-execution-impacts`

### Step 3: Risk Margin Calculator [depends_on: paired-market-scanner]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Audits margin utilization limits, collateral safety, and maximum drawdown risk.
Expected: `margin-safety-bounds`

### Step 4: Trade Execution Engine [depends_on: order-book-simulator, risk-margin-calculator]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Executes execution orders across exchange endpoints and records trades.
Expected: `arbitrage-execution-receipts`

### Step 5: KG Persistence [depends_on: trade-execution-engine]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Polymarket Paired Arbitrage results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Paired Market Scanner
- **After level 0:** Step 2 — Order Book Simulator; Step 3 — Risk Margin Calculator
- **After level 1:** Step 4 — Trade Execution Engine
- **After level 2:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
