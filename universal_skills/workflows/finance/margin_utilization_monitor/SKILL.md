---
name: margin_utilization_monitor
description: >-
  Parallel execution workflow for margin utilization monitor using the Unified Parallel Engine
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
  tool_assignments:
    data-fetcher: [graph_query, sx_search]
    compute-engine: [graph_analyze]
    risk-assessor: [graph_query, graph_analyze]
tags: [finance, margin-utilization-monitor]
concept: CONCEPT:EE-011
---

# Margin Utilization Monitor Workflow

**CONCEPT:EE-011**

Parallel execution workflow for margin utilization monitor using the Unified Parallel Engine

## Steps

### Step 1: Fetch Margin
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute fetch margin operations for the Margin Utilization Monitor workflow.
Expected: `fetch_margin_artifacts`

### Step 2: Calc Utilization [depends_on: fetch_margin]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute calc utilization operations for the Margin Utilization Monitor workflow.
Expected: `calc_utilization_artifacts`

### Step 3: Alert If 80 [depends_on: calc_utilization]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute alert if 80 operations for the Margin Utilization Monitor workflow.
Expected: `alert_if_80_artifacts`

### Step 4: KG Persistence [depends_on: alert_if_80]
**Agent**: `risk-assessor`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Margin Utilization Monitor results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fetch Margin
- **After level 0:** Step 2 — Calc Utilization
- **After level 1:** Step 3 — Alert If 80
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
