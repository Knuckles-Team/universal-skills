---
name: continuous-risk-monitor
skill_type: workflow
description: >-
  Parallel execution workflow for continuous risk monitor using the Unified Parallel Engine
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
tags: [finance, continuous-risk-monitor]
concept: CONCEPT:EE-011
metadata:
  version: '1.2.1'
---

# Continuous Risk Monitor Workflow

**CONCEPT:EE-011**

Parallel execution workflow for continuous risk monitor using the Unified Parallel Engine

## Steps

### Step 1: Drawdown Check
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute drawdown check operations for the Continuous Risk Monitor workflow.
Expected: `drawdown_check_artifacts`

### Step 2: Daily Loss
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute daily loss operations for the Continuous Risk Monitor workflow.
Expected: `daily_loss_artifacts`

### Step 3: Regime Shift
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute regime shift operations for the Continuous Risk Monitor workflow.
Expected: `regime_shift_artifacts`

### Step 4: Position Limits
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute position limits operations for the Continuous Risk Monitor workflow.
Expected: `position_limits_artifacts`

### Step 5: Circuit Breaker [depends_on: drawdown_check, daily_loss, regime_shift, position_limits]
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute circuit breaker operations for the Continuous Risk Monitor workflow.
Expected: `circuit_breaker_artifacts`

### Step 6: KG Persistence [depends_on: circuit_breaker]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Continuous Risk Monitor results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Drawdown Check; Step 2 — Daily Loss; Step 3 — Regime Shift; Step 4 — Position Limits
- **After level 0:** Step 5 — Circuit Breaker
- **After level 1:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
