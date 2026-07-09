---
name: options_volatility_surface
description: >-
  Fetches multi-expiry options chain price metrics, fits implied volatility surface curves, and identifies skew arbitrage.
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
tags: [options, volatility, iv, skew]
concept: CONCEPT:EE-011
---

# Options Volatility Surface Workflow

**CONCEPT:EE-011**

Fetches multi-expiry options chain price metrics, fits implied volatility surface curves, and identifies skew arbitrage.

## Steps

### Step 1: Options Feed Collector
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Fetches option chain price logs and strike parameters across multiple expiries.
Expected: `raw-options-chain-feeds`

### Step 2: Iv Surface Fitter [depends_on: options-feed-collector]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Fits an implied volatility surface and calculates volatility smiles.
Expected: `implied-volatility-surface`

### Step 3: Anomaly Detector [depends_on: iv-surface-fitter]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Identifies mispriced options contracts and volatility skew anomalies.
Expected: `volatility-skew-anomalies`

### Step 4: Arbitrage Executor [depends_on: anomaly-detector]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Proposes volatility trade executions to profit from the spreads.
Expected: `options-arbitrage-orders`

### Step 5: KG Persistence [depends_on: arbitrage-executor]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Options Volatility Surface results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Options Feed Collector
- **After level 0:** Step 2 — Iv Surface Fitter
- **After level 1:** Step 3 — Anomaly Detector
- **After level 2:** Step 4 — Arbitrage Executor
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
