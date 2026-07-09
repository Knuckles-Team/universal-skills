---
name: cross-asset-correlation
description: >-
  Collects multi-ticker price data, constructs rolling correlation matrices, flags eigen anomalies, and adjusts portfolio scale limits.
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
tags: [correlation, cross-asset, matrix, risk]
concept: CONCEPT:EE-011
---

# Cross Asset Correlation Workflow

**CONCEPT:EE-011**

Collects multi-ticker price data, constructs rolling correlation matrices, flags eigen anomalies, and adjusts portfolio scale limits.

## Steps

### Step 1: Multi Ticker Collector
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Collects price feeds for spot equities, commodities, and currencies concurrently.
Expected: `multi-asset-historical-prices`

### Step 2: Correlation Matrix Fitter [depends_on: multi-ticker-collector]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Computes standard rolling correlation matrices and eigenvalues.
Expected: `rolling-correlation-matrices`

### Step 3: Eigen Anomaly Detector [depends_on: correlation-matrix-fitter]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Flags breakdowns in historical sector correlations.
Expected: `eigenvalue-breakdown-signals`

### Step 4: Risk Exposure Adjuster [depends_on: eigen-anomaly-detector]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Updates portfolio limit scales to mitigate systemic contagion.
Expected: `adjusted-portfolio-limits`

### Step 5: KG Persistence [depends_on: risk-exposure-adjuster]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Cross Asset Correlation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Multi Ticker Collector
- **After level 0:** Step 2 — Correlation Matrix Fitter
- **After level 1:** Step 3 — Eigen Anomaly Detector
- **After level 2:** Step 4 — Risk Exposure Adjuster
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
