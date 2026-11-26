---
name: cross-asset-correlation
skill_type: workflow
description: >-
  Collects multi-ticker price data, constructs rolling correlation matrices, flags eigen anomalies, and adjusts portfolio scale limits.
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
tags: [correlation, cross-asset, matrix, risk]
concept: CONCEPT:EE-011
metadata:
  version: '1.6.2'
---

# Cross Asset Correlation Workflow

**CONCEPT:EE-011**

Collects multi-ticker price data, constructs rolling correlation matrices, flags eigen anomalies, and adjusts portfolio scale limits.

## Steps

1. Collect price feeds for equities, commodities and currencies with `graph_query` and `sx_search` (Step 1). Verify that `multi-asset-historical-prices` covers every requested ticker over the same date range.
2. Fit the rolling correlation matrices and eigenvalues with `graph_analyze` (Step 2). Verify that `rolling-correlation-matrices` is square and symmetric for each window.
3. Detect eigenvalue breakdowns in sector correlations (Step 3). Verify that `eigenvalue-breakdown-signals` lists each flagged sector or states that none breached the threshold.
4. Update portfolio limit scales from the signals with `graph_write` (Step 4). Verify that `adjusted-portfolio-limits` shows a changed limit for every flagged sector.
5. Persist the results with `graph_write` (Step 5). Verify that `graph_query` returns the stored correlation node.

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

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Correlation matrix has NaN entries | A ticker has missing history or misaligned dates | Drop or forward-fill the short series in Step 1 and refit the matrices |
| No anomalies flagged in a known stress period | The rolling window is too long to react | Shorten the window in Step 2 and compare the eigenvalue series against the stress dates |
| Limits not updated | `graph_write` failed or no signal crossed the threshold | Check the Step 3 signals, confirm access with `graph_query`, and rerun Step 4 on the saved signals |


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

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
