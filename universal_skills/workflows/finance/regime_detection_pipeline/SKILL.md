---
name: regime_detection_pipeline
description: >-
  Collects pricing indicators, extracts structural features, fits Hidden Markov Model classifiers, and adapts strategy params to structural shifts.
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
tags: [regime, hmm, volatility, classification]
concept: CONCEPT:EE-011
---

# Regime Detection Pipeline Workflow

**CONCEPT:EE-011**

Collects pricing indicators, extracts structural features, fits Hidden Markov Model classifiers, and adapts strategy params to structural shifts.

## Steps

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

## Output
- Regime Detection Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
