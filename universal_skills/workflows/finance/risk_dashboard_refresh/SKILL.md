---
name: risk_dashboard_refresh
description: >-
  Pulls daily assets returns, computes Value-at-Risk parameters, extracts maximum drawdown ratios, and updates dashboard.
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
tags: [risk, dashboard, var, drawdown]
concept: CONCEPT:EE-011
---

# Risk Dashboard Refresh Workflow

**CONCEPT:EE-011**

Pulls daily assets returns, computes Value-at-Risk parameters, extracts maximum drawdown ratios, and updates dashboard.

## Steps

### Step 1: Portfolio Returns Fetcher
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Fetches daily rolling returns logs for active holdings.
Expected: `historical-daily-returns`

### Step 2: Var Calculator [depends_on: portfolio-returns-fetcher]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Computes Parametric and Monte Carlo Value-at-Risk (VaR) parameters.
Expected: `value-at-risk-metrics`

### Step 3: Drawdown Tracker [depends_on: portfolio-returns-fetcher]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Measures rolling drawdown, Sharpe, and Sortino statistics.
Expected: `drawdown-and-performance-stats`

### Step 4: Dashboard Synthesis [depends_on: var-calculator, drawdown-tracker]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Compiles metrics and updates dashboard files.
Expected: `fused-risk-tearsheet`

### Step 5: KG Persistence [depends_on: dashboard-synthesis]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Risk Dashboard Refresh results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
