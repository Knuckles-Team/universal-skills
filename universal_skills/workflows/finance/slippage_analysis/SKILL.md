---
name: slippage_analysis
description: >-
  Parallel execution workflow for slippage analysis using the Unified Parallel Engine
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
tags: [finance, slippage-analysis]
concept: CONCEPT:EE-011
---

# Slippage Analysis Workflow

**CONCEPT:EE-011**

Parallel execution workflow for slippage analysis using the Unified Parallel Engine

## Steps

### Step 1: Pull Fills
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute pull fills operations for the Slippage Analysis workflow.
Expected: `pull_fills_artifacts`

### Step 2: Compare To Signal Price [depends_on: pull_fills]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute compare to signal price operations for the Slippage Analysis workflow.
Expected: `compare_to_signal_price_artifacts`

### Step 3: Calc Slippage Stats [depends_on: compare_to_signal_price]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute calc slippage stats operations for the Slippage Analysis workflow.
Expected: `calc_slippage_stats_artifacts`

### Step 4: Optimize [depends_on: calc_slippage_stats]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute optimize operations for the Slippage Analysis workflow.
Expected: `optimize_artifacts`

### Step 5: KG Persistence [depends_on: optimize]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Slippage Analysis results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
