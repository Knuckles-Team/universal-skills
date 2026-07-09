---
name: trading-signal-fusion
skill_type: workflow
description: >-
  Parallel execution workflow for trading signal fusion using the Unified Parallel Engine
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
tags: [finance, trading-signal-fusion]
concept: CONCEPT:EE-011
metadata:
  version: '1.0.2'
---

# Trading Signal Fusion Workflow

**CONCEPT:EE-011**

Parallel execution workflow for trading signal fusion using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Signal Type Technical
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute fan out per signal type technical operations for the Trading Signal Fusion workflow.
Expected: `fan_out_per_signal_type_technical_artifacts`

### Step 2: Fundamental
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute fundamental operations for the Trading Signal Fusion workflow.
Expected: `fundamental_artifacts`

### Step 3: Sentiment
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute sentiment operations for the Trading Signal Fusion workflow.
Expected: `sentiment_artifacts`

### Step 4: Meta Model [depends_on: fan_out_per_signal_type_technical, fundamental, sentiment]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute meta model operations for the Trading Signal Fusion workflow.
Expected: `meta_model_artifacts`

### Step 5: KG Persistence [depends_on: meta_model]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Trading Signal Fusion results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Signal Type Technical; Step 2 — Fundamental; Step 3 — Sentiment
- **After level 0:** Step 4 — Meta Model
- **After level 1:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
