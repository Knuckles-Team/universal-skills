---
name: portfolio_tearsheet_gen
description: >-
  Parallel execution workflow for portfolio tearsheet gen using the Unified Parallel Engine
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
tags: [finance, portfolio-tearsheet-gen]
concept: CONCEPT:EE-011
---

# Portfolio Tearsheet Gen Workflow

**CONCEPT:EE-011**

Parallel execution workflow for portfolio tearsheet gen using the Unified Parallel Engine

## Steps

### Step 1: Returns
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute returns operations for the Portfolio Tearsheet Gen workflow.
Expected: `returns_artifacts`

### Step 2: Drawdown
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute drawdown operations for the Portfolio Tearsheet Gen workflow.
Expected: `drawdown_artifacts`

### Step 3: Monthly Heatmap
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute monthly heatmap operations for the Portfolio Tearsheet Gen workflow.
Expected: `monthly_heatmap_artifacts`

### Step 4: Monte Carlo
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute monte carlo operations for the Portfolio Tearsheet Gen workflow.
Expected: `monte_carlo_artifacts`

### Step 5: Pdf Report [depends_on: returns, drawdown, monthly_heatmap, monte_carlo]
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute pdf report operations for the Portfolio Tearsheet Gen workflow.
Expected: `pdf_report_artifacts`

### Step 6: KG Persistence [depends_on: pdf_report]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Portfolio Tearsheet Gen results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Returns; Step 2 — Drawdown; Step 3 — Monthly Heatmap; Step 4 — Monte Carlo
- **After level 0:** Step 5 — Pdf Report
- **After level 1:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
