---
name: qlib_factor_backtest
description: >-
  Parallel execution workflow for qlib factor backtest using the Unified Parallel Engine
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
tags: [finance, qlib-factor-backtest]
concept: CONCEPT:EE-011
---

# Qlib Factor Backtest Workflow

**CONCEPT:EE-011**

Parallel execution workflow for qlib factor backtest using the Unified Parallel Engine

## Steps

### Step 1: Prepare Data
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute prepare data operations for the Qlib Factor Backtest workflow.
Expected: `prepare_data_artifacts`

### Step 2: Fit Model [depends_on: prepare_data]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute fit model operations for the Qlib Factor Backtest workflow.
Expected: `fit_model_artifacts`

### Step 3: Backtest [depends_on: fit_model]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute backtest operations for the Qlib Factor Backtest workflow.
Expected: `backtest_artifacts`

### Step 4: Ic Analysis [depends_on: backtest]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute ic analysis operations for the Qlib Factor Backtest workflow.
Expected: `ic_analysis_artifacts`

### Step 5: KG Persistence [depends_on: ic_analysis]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Qlib Factor Backtest results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
