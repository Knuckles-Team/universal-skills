---
name: crypto-arbitrage
skill_type: workflow
description: >-
  >-
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
tags: [finance, crypto, arbitrage, stat-arb]
concept: CONCEPT:EE-011
metadata:
  version: '1.1.0'
---

# Crypto Arbitrage Workflow

**CONCEPT:EE-011**

>-

## Steps

### Step 1: Pair Scan
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Identify cointegrated pairs across exchanges.
Tool: Route to agent-utilities `cross_market_arb.py` CointegrationAnalyzer.

### Step 2: Ou Estimate
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Ornstein-Uhlenbeck parameter estimation for mean-reversion speed.

### Step 3: On Chain Check
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Check whale alerts, funding rates, DEX volumes.
Tool: Route to agent-utilities `crypto_connector.py` OnChainAnalytics.

### Step 4: Risk Check
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Pre-trade risk validation.
Tool: `emerald_risk(action="drawdown_check")`

### Step 5: Execute Arb
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Submit paired orders via exchange backend.
Tool: `emerald_orders(action="submit", ...)` for both legs.

### Step 6: KG Persistence [depends_on: execute-arb]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Crypto Arbitrage results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Pair Scan; Step 2 — Ou Estimate; Step 3 — On Chain Check; Step 4 — Risk Check; Step 5 — Execute Arb
- **After level 0:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
