---
name: crypto-arbitrage
skill_type: workflow
description: >-
  Parallel execution workflow for crypto arbitrage using the Unified Parallel Engine
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
  version: '1.6.2'
---

# Crypto Arbitrage Workflow

**CONCEPT:EE-011**

>-

## Steps

1. Scan exchanges for cointegrated pairs with the meristem `cross_market_arb.py` CointegrationAnalyzer (Step 1). Verify that the output lists at least one pair with a cointegration statistic.
2. Estimate Ornstein-Uhlenbeck mean-reversion parameters for each pair with `graph_analyze` (Step 2). Verify that each pair has a finite reversion speed and half-life.
3. Check whale alerts, funding rates and DEX volumes with the meristem `crypto_connector.py` OnChainAnalytics (Step 3). Verify that the output carries a value for each of the three signals.
4. Validate pre-trade risk with `emerald_risk_drawdown_check()` (Step 4). Verify that the result is an explicit pass before any order is placed.
5. Submit both legs with `emerald_orders_submit(...)` only after the risk check passed (Step 5). Verify that both legs return an order ID and a status.
6. Persist the run with `graph_write` (Step 6). Verify that `graph_query` returns the stored arbitrage node.

### Step 1: Pair Scan
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Identify cointegrated pairs across exchanges.
Tool: Route to meristem `cross_market_arb.py` CointegrationAnalyzer.

### Step 2: Ou Estimate
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Ornstein-Uhlenbeck parameter estimation for mean-reversion speed.

### Step 3: On Chain Check
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Check whale alerts, funding rates, DEX volumes.
Tool: Route to meristem `crypto_connector.py` OnChainAnalytics.

### Step 4: Risk Check
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Pre-trade risk validation.
Tool: `emerald_risk_drawdown_check()`

### Step 5: Execute Arb
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Submit paired orders via exchange backend.
Tool: `emerald_orders_submit(...)` for both legs.

### Step 6: KG Persistence [depends_on: execute-arb]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Risk check fails | Drawdown or exposure limit is breached | Do not submit orders, reduce position size, and rerun `emerald_risk_drawdown_check()` |
| Only one leg fills | Liquidity or latency differs between exchanges | Close or hedge the filled leg with `emerald_orders_submit(...)` and record the unfilled leg in the report |
| No pairs found | The cointegration window is too short or exchanges have no overlap | Extend the lookback window in Step 1 or add exchanges to the scan |
| Order submission is rejected | Credentials or balance are insufficient | Check the exchange credentials and balances, then resubmit with a corrected size |


## Output
- Crypto Arbitrage results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Pair Scan; Step 2 — Ou Estimate; Step 3 — On Chain Check; Step 4 — Risk Check; Step 5 — Execute Arb
- **After level 0:** Step 6 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
