---
name: benchmark-tracking-error
skill_type: workflow
description: >-
  Pulls daily benchmark indices, calculates active share tracking error, decomposes performance style, and dispatches drift alerts.
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
tags: [tracking-error, active-share, style-attribution, drift]
concept: CONCEPT:EE-011
metadata:
  version: '1.6.2'
---

# Benchmark Tracking Error Workflow

**CONCEPT:EE-011**

Pulls daily benchmark indices, calculates active share tracking error, decomposes performance style, and dispatches drift alerts.

## Steps

1. Fetch benchmark and holdings returns by running Step 1 with `graph_query` and `sx_search`. Verify that `benchmark-price-returns` has aligned daily dates for holdings and the index.
2. Compute tracking error by running Step 2 with `graph_analyze`. Verify that `rolling-tracking-errors` contains both tracking error and active share values.
3. Attribute returns by running Step 3 with `graph_analyze`. Verify that `style-returns-attribution` splits asset selection from style effects and the parts sum to the active return.
4. Dispatch drift alerts by running Step 4 with `document_tools`. Verify that `portfolio-drift-verdicts` lists each bound checked and whether it was breached.
5. Persist the outputs by running Step 5 with `graph_write`. Verify that a `graph_query` for the new nodes returns the verdicts.


### Step 1: Benchmark Returns Collector
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Fetches daily rolling returns logs for active holdings and indices.
Expected: `benchmark-price-returns`

### Step 2: Tracking Error Calculator [depends_on: benchmark-returns-collector]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Computes rolling tracking error and active share indexes.
Expected: `rolling-tracking-errors`

### Step 3: Return Attribution Engine [depends_on: tracking-error-calculator]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Decomposes portfolio returns into asset selection and style attribution.
Expected: `style-returns-attribution`

### Step 4: Drift Alert Dispatch [depends_on: return-attribution-engine]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Checks target bounds and dispatches alerts on breach.
Expected: `portfolio-drift-verdicts`

### Step 5: KG Persistence [depends_on: drift-alert-dispatch]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Return series misaligned | Holdings and index have different trading calendars | Reindex both series to the shared dates before Step 2 and drop non-overlapping days |
| Tracking error is NaN | Fewer observations than the rolling window | Shorten the window or extend the lookback and re-run Step 2 |
| Attribution does not sum | Style factors incomplete | Add the missing style factor returns and re-run Step 3 |
| Alerts not dispatched | Alert channel not configured | Confirm the delivery tool is available and write the verdicts to the report instead |

## Output
- Benchmark Tracking Error results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Benchmark Returns Collector
- **After level 0:** Step 2 — Tracking Error Calculator
- **After level 1:** Step 3 — Return Attribution Engine
- **After level 2:** Step 4 — Drift Alert Dispatch
- **After level 3:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
