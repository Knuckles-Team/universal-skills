---
name: strategy-export
skill_type: workflow
description: >-
  Parallel execution workflow for strategy export using the Unified Parallel Engine
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
tags: [finance, strategy, export, deployment]
concept: CONCEPT:EE-011
metadata:
  version: '1.1.0'
---

# Strategy Export Workflow

**CONCEPT:EE-011**

>-

## Steps

### Step 1: Select Strategy
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Pick a validated strategy from the Knowledge Graph.
Tool: `emerald_strategy(action="list")`

### Step 2: Export
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Convert to target format (PineScript/MQL5/TDX).
Tool: `emerald_strategy(action="export", strategy_id=..., format="pinescript")`

### Step 3: Deploy Freqtrade
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Deploy to freqtrade in paper mode for validation.
Tool: Route to freqtrade backend for dry-run.

### Step 4: Share
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Publish to community strategy registry.
Tool: Route to agent-utilities `strategy_sharing.py`.

### Step 5: KG Persistence [depends_on: share]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Strategy Export results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Select Strategy; Step 2 — Export; Step 3 — Deploy Freqtrade; Step 4 — Share
- **After level 0:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
