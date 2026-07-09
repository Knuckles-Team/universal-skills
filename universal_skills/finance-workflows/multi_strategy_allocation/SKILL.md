---
name: multi_strategy_allocation
description: >-
  Parallel execution workflow for multi strategy allocation using the Unified Parallel Engine
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
tags: [finance, multi-strategy-allocation]
concept: CONCEPT:EE-011
---

# Multi Strategy Allocation Workflow

**CONCEPT:EE-011**

Parallel execution workflow for multi strategy allocation using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Strategy Performance
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute fan out per strategy performance operations for the Multi Strategy Allocation workflow.
Expected: `fan_out_per_strategy_performance_artifacts`

### Step 2: Risk Metrics [depends_on: fan_out_per_strategy_performance]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute risk metrics operations for the Multi Strategy Allocation workflow.
Expected: `risk_metrics_artifacts`

### Step 3: Kelly Sizing [depends_on: risk_metrics]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute kelly sizing operations for the Multi Strategy Allocation workflow.
Expected: `kelly_sizing_artifacts`

### Step 4: Combine [depends_on: kelly_sizing]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute combine operations for the Multi Strategy Allocation workflow.
Expected: `combine_artifacts`

### Step 5: KG Persistence [depends_on: combine]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Multi Strategy Allocation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Strategy Performance
- **After level 0:** Step 2 — Risk Metrics
- **After level 1:** Step 3 — Kelly Sizing
- **After level 2:** Step 4 — Combine
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
