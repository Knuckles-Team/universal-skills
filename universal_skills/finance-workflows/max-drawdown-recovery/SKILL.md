---
name: max-drawdown-recovery
skill_type: workflow
description: >-
  Parallel execution workflow for max drawdown recovery using the Unified Parallel Engine
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
tags: [finance, max-drawdown-recovery]
concept: CONCEPT:EE-011
metadata:
  version: '1.2.0'
---

# Max Drawdown Recovery Workflow

**CONCEPT:EE-011**

Parallel execution workflow for max drawdown recovery using the Unified Parallel Engine

## Steps

### Step 1: Detect Dd
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute detect dd operations for the Max Drawdown Recovery workflow.
Expected: `detect_dd_artifacts`

### Step 2: Pause Strategies [depends_on: detect_dd]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute pause strategies operations for the Max Drawdown Recovery workflow.
Expected: `pause_strategies_artifacts`

### Step 3: Hedge [depends_on: pause_strategies]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute hedge operations for the Max Drawdown Recovery workflow.
Expected: `hedge_artifacts`

### Step 4: Monitor Recovery [depends_on: hedge]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute monitor recovery operations for the Max Drawdown Recovery workflow.
Expected: `monitor_recovery_artifacts`

### Step 5: Resume [depends_on: monitor_recovery]
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute resume operations for the Max Drawdown Recovery workflow.
Expected: `resume_artifacts`

### Step 6: KG Persistence [depends_on: resume]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Max Drawdown Recovery results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Detect Dd
- **After level 0:** Step 2 — Pause Strategies
- **After level 1:** Step 3 — Hedge
- **After level 2:** Step 4 — Monitor Recovery
- **After level 3:** Step 5 — Resume
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
