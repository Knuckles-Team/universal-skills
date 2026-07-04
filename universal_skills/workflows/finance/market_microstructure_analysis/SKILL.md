---
name: market_microstructure_analysis
description: >-
  Audits millisecond order book snapshot logs, computes VPIN metrics, decomposes spreads, and aggregates impact reports.
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
tags: [microstructure, order-book, vpin, slippage]
concept: CONCEPT:EE-011
---

# Market Microstructure Analysis Workflow

**CONCEPT:EE-011**

Audits millisecond order book snapshot logs, computes VPIN metrics, decomposes spreads, and aggregates impact reports.

## Steps

### Step 1: Book Snapshot Crawlers
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Collects millisecond order book snapshot logs.
Expected: `order-book-snapshots`

### Step 2: Flow Toxicity Calculator [depends_on: book-snapshot-crawlers]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Calculates VPIN and buy-sell order flow imbalance.
Expected: `volume-toxicity-signals`

### Step 3: Spread Decomposition [depends_on: flow-toxicity-calculator]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Decomposes bid-ask spread into inventory and adverse selection.
Expected: `decomposed-spread-metrics`

### Step 4: Impact Report [depends_on: spread-decomposition]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Compiles execution cost optimization recommendation cards.
Expected: `microstructure-impact-tearsheet`

### Step 5: KG Persistence [depends_on: impact-report]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Market Microstructure Analysis results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Book Snapshot Crawlers
- **After level 0:** Step 2 — Flow Toxicity Calculator
- **After level 1:** Step 3 — Spread Decomposition
- **After level 2:** Step 4 — Impact Report
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
