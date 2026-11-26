---
name: risk-dashboard-refresh
skill_type: workflow
description: >-
  Pulls daily assets returns, computes Value-at-Risk parameters, extracts maximum drawdown ratios, and updates dashboard.
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
tags: [risk, dashboard, var, drawdown]
concept: CONCEPT:EE-011
metadata:
  version: '1.6.2'
---

# Risk Dashboard Refresh Workflow

**CONCEPT:EE-011**

Pulls daily assets returns, computes Value-at-Risk parameters, extracts maximum drawdown ratios, and updates dashboard.

## Steps

1. Fetch daily rolling returns for active holdings with `graph_query` and `sx_search`. Verify that `historical-daily-returns` includes every active holding up to the latest trading day.
2. Compute parametric and Monte Carlo VaR with `graph_analyze`. Verify that `value-at-risk-metrics` reports both methods and the confidence level.
3. Measure rolling drawdown, Sharpe and Sortino with `graph_query` and `graph_analyze`. Verify that `drawdown-and-performance-stats` covers the same window as the VaR step.
4. Compile the metrics and update the dashboard files using `graph_write` and `document_tools`. Verify that `fused-risk-tearsheet` shows the refreshed timestamp and both metric sets.
5. Persist the results as typed nodes and edges with `graph_write`. Verify that a follow-up `graph_query` returns the new nodes linked to existing domain entities.

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

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Returns end before the latest day | The data source lags | Refresh the source with `sx_search` or label the dashboard with the actual last date. |
| VaR methods disagree widely | Short return history skews the Monte Carlo run | Lengthen the history and recompute with `graph_analyze`. |
| Dashboard file is not updated | The write step lacked the dashboard path | Supply the dashboard target path to `document_tools` and write again. |
| `graph_write` persistence is rejected | A node has no type or no link target | Re-issue `graph_write` with a typed node and an edge to an entity located first with `graph_query`. |

## Output
- Risk Dashboard Refresh results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Portfolio Returns Fetcher
- **After level 0:** Step 2 — Var Calculator; Step 3 — Drawdown Tracker
- **After level 1:** Step 4 — Dashboard Synthesis
- **After level 2:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
