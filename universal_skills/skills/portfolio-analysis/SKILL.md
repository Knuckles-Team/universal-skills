---
name: portfolio-analysis
skill_type: workflow
description: >-
  Parallel execution workflow for portfolio analysis using the Unified Parallel Engine
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
  tool_assignments:
    data-fetcher: [graph_query, sx_search]
    compute-engine: [graph_analyze]
    risk-assessor: [graph_query, graph_analyze]
tags: [finance, analysis, portfolio]
concept: CONCEPT:EE-011
metadata:
  version: '1.7.0'
---

# Portfolio Analysis Workflow

**CONCEPT:EE-011**

>-

## Steps

1. Extract the latest holdings and benchmark data with `graph_query` and `sx_search`. Verify that the holdings list is non-empty and carries a retrieval date.
2. Compute risk metrics, exposures and VaR with `graph_analyze`. Verify that each metric is calculated from the extracted holdings and reports its window.
3. Synthesize the metrics and holdings into a markdown report with `graph_query` and `graph_analyze`. Verify that the report lists every holding and each risk metric.
4. Persist the results as typed nodes and edges with `graph_write`. Verify that a follow-up `graph_query` returns the new nodes linked to existing domain entities.

### Step 1: Data Extractor
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Extract the latest holding data from the portfolio system and fetch benchmark data.

### Step 2: Risk Analyzer
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Calculate risk metrics, exposures, and VaR based on the extracted holding data.

### Step 3: Report Generator
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Synthesize the risk metrics and holding data into a formatted markdown report.

### Step 4: KG Persistence [depends_on: report-generator]
**Agent**: `risk-assessor`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Holdings list is empty | The portfolio system returned no positions | Re-query with `graph_query` using the correct portfolio identifier and check the source system for access errors. |
| VaR cannot be computed | Price history is too short for the window | Extend the history with `sx_search` or shorten the VaR window and state the change in the report. |
| `graph_write` persistence is rejected | A node has no type or no link target | Re-issue `graph_write` with a typed node and an edge to an entity located first with `graph_query`. |
| `graph_orchestrate` cannot run the DAG | arbora is unreachable | Skip the offload and execute the steps natively in dependency order as described under `## Execution`. |

## Output
- Portfolio Analysis results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Data Extractor; Step 2 — Risk Analyzer; Step 3 — Report Generator
- **After level 0:** Step 4 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
