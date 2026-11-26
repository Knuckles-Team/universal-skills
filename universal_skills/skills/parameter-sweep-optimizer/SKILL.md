---
name: parameter-sweep-optimizer
skill_type: workflow
description: >-
  Spawns 25 parallel parameter sweep configurations, extracts performance curves, plots response surfaces, and designates optimal param configs.
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
tags: [parameter-sweep, optimization, grid-search, visualization]
concept: CONCEPT:EE-011
metadata:
  version: '1.6.2'
---

# Parameter Sweep Optimizer Workflow

**CONCEPT:EE-011**

Spawns 25 parallel parameter sweep configurations, extracts performance curves, plots response surfaces, and designates optimal param configs.

## Steps

1. Spawn 25 configurations with `graph_query` and `sx_search`. Verify that `multi-parameter-backtest-records` has 25 entries.
2. Extract metrics with `graph_analyze`. Verify that `extracted-response-metrics` covers each node.
3. Plot the response surface with `graph_analyze`. Verify that `volatility-response-surface-plot` shows stable basins.
4. Select parameters with `graph_write`. Verify that `finalized-parameter-configs` is registered.
5. Persist with `graph_write`. Verify that a `graph_query` returns the new nodes.

### Step 1: Grid Search Sweeper
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Spawns 25 parallel parameter configuration models.
Expected: `multi-parameter-backtest-records`

### Step 2: Metric Extractor [depends_on: grid-search-sweeper]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Extracts performance indicators and fit scores for each sweep node.
Expected: `extracted-response-metrics`

### Step 3: Surface Plotter [depends_on: metric-extractor]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Generates a 3D parameter response surface map to identify stable basins.
Expected: `volatility-response-surface-plot`

### Step 4: Config Selector [depends_on: surface-plotter]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Selects the parameters that minimize overfitting and registers them.
Expected: `finalized-parameter-configs`

### Step 5: KG Persistence [depends_on: config-selector]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Missing runs | Worker crashed | Identify missing configuration ids and re-run only those sweeps |
| Surface noisy | Overfit | Choose parameters from the centre of a smooth basin on the plotted surface rather than the peak |
| Registration fails | Schema | Add the missing required fields to the `graph_write` payload and repeat the write |

## Output
- Parameter Sweep Optimizer results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Grid Search Sweeper
- **After level 0:** Step 2 — Metric Extractor
- **After level 1:** Step 3 — Surface Plotter
- **After level 2:** Step 4 — Config Selector
- **After level 3:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
