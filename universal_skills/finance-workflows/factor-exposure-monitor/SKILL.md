---
name: factor-exposure-monitor
description: >-
  Parallel execution workflow for factor exposure monitor using the Unified Parallel Engine
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
tags: [finance, factor-exposure-monitor]
concept: CONCEPT:EE-011
---

# Factor Exposure Monitor Workflow

**CONCEPT:EE-011**

Parallel execution workflow for factor exposure monitor using the Unified Parallel Engine

## Steps

### Step 1: Momentum
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute momentum operations for the Factor Exposure Monitor workflow.
Expected: `momentum_artifacts`

### Step 2: Value
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute value operations for the Factor Exposure Monitor workflow.
Expected: `value_artifacts`

### Step 3: Size
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute size operations for the Factor Exposure Monitor workflow.
Expected: `size_artifacts`

### Step 4: Quality
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute quality operations for the Factor Exposure Monitor workflow.
Expected: `quality_artifacts`

### Step 5: Drift Alerts [depends_on: momentum, value, size, quality]
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute drift alerts operations for the Factor Exposure Monitor workflow.
Expected: `drift_alerts_artifacts`

### Step 6: KG Persistence [depends_on: drift_alerts]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Factor Exposure Monitor results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Momentum; Step 2 — Value; Step 3 — Size; Step 4 — Quality
- **After level 0:** Step 5 — Drift Alerts
- **After level 1:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
