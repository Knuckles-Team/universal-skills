---
name: benchmark-tracking-error
description: >-
  Pulls daily benchmark indices, calculates active share tracking error, decomposes performance style, and dispatches drift alerts.
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
tags: [tracking-error, active-share, style-attribution, drift]
concept: CONCEPT:EE-011
---

# Benchmark Tracking Error Workflow

**CONCEPT:EE-011**

Pulls daily benchmark indices, calculates active share tracking error, decomposes performance style, and dispatches drift alerts.

## Steps

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

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
