---
name: regime-detection-pipeline
skill_type: workflow
description: >-
  Collects pricing indicators, extracts structural features, fits Hidden Markov Model classifiers, and adapts strategy params to structural shifts.
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
tags: [regime, hmm, volatility, classification]
concept: CONCEPT:EE-011
metadata:
  version: '1.7.0'
---

# Regime Detection Pipeline Workflow

**CONCEPT:EE-011**

Collects pricing indicators, extracts structural features, fits Hidden Markov Model classifiers, and adapts strategy params to structural shifts.

## Steps

1. Collect tick volumes, bid-ask spreads and rolling volatilities with `graph_query` and `sx_search`. Verify that `market-regime-raw-data` spans a continuous period without gaps.
2. Normalize features and compute volatility and trend indicators with `graph_analyze`. Verify that `structured-regime-features` has no NaN values.
3. Fit a Hidden Markov Model with `graph_query` and `graph_analyze` to classify market state. Verify that `hmm-state-classifications` assigns a state to every period.
4. Modify strategy parameters from the detected state using `graph_write`. Verify that `adapted-parameters-configs` records the state that triggered each change.
5. Persist the results as typed nodes and edges with `graph_write`. Verify that a follow-up `graph_query` returns the new nodes linked to existing domain entities.

### Step 1: Data Collector
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Collects tick volumes, bid-ask spreads, and rolling volatilities.
Expected: `market-regime-raw-data`

### Step 2: Feature Extractor [depends_on: data-collector]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Normalizes features and computes rolling volatility and trend indicators.
Expected: `structured-regime-features`

### Step 3: Hmm Regime Fitter [depends_on: feature-extractor]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Fits a Hidden Markov Model (HMM) to classify market state.
Expected: `hmm-state-classifications`

### Step 4: Regime Adapter [depends_on: hmm-regime-fitter]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Triggers strategy parameters modification based on the detected state.
Expected: `adapted-parameters-configs`

### Step 5: KG Persistence [depends_on: regime-adapter]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Raw data has gaps | The source skipped sessions | Fill the gap with another `sx_search` source or trim the period to the continuous range. |
| HMM fails to converge | Too many states for the data volume | Reduce the number of states in the `graph_analyze` inputs and refit. |
| States flip every period | Features are too noisy | Smooth the features with a longer rolling window and refit. |
| `graph_write` persistence is rejected | A node has no type or no link target | Re-issue `graph_write` with a typed node and an edge to an entity located first with `graph_query`. |

## Output
- Regime Detection Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Data Collector
- **After level 0:** Step 2 — Feature Extractor
- **After level 1:** Step 3 — Hmm Regime Fitter
- **After level 2:** Step 4 — Regime Adapter
- **After level 3:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
