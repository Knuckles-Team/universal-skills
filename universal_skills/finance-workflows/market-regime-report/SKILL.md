---
name: market-regime-report
skill_type: workflow
description: >-
  Parallel execution workflow for market regime report using the Unified Parallel Engine
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
tags: [finance, market-regime-report]
concept: CONCEPT:EE-011
metadata:
  version: '1.2.1'
---

# Market Regime Report Workflow

**CONCEPT:EE-011**

Parallel execution workflow for market regime report using the Unified Parallel Engine

## Steps

### Step 1: Volatility Regime
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute volatility regime operations for the Market Regime Report workflow.
Expected: `volatility_regime_artifacts`

### Step 2: Trend Regime
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute trend regime operations for the Market Regime Report workflow.
Expected: `trend_regime_artifacts`

### Step 3: Correlation Regime
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute correlation regime operations for the Market Regime Report workflow.
Expected: `correlation_regime_artifacts`

### Step 4: Daily Brief [depends_on: volatility_regime, trend_regime, correlation_regime]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute daily brief operations for the Market Regime Report workflow.
Expected: `daily_brief_artifacts`

### Step 5: KG Persistence [depends_on: daily_brief]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Market Regime Report results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Volatility Regime; Step 2 — Trend Regime; Step 3 — Correlation Regime
- **After level 0:** Step 4 — Daily Brief
- **After level 1:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
