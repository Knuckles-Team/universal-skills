---
name: finrl_training_pipeline
description: >-
  Parallel execution workflow for finrl training pipeline using the Unified Parallel Engine
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
tags: [finance, finrl-training-pipeline]
concept: CONCEPT:EE-011
---

# Finrl Training Pipeline Workflow

**CONCEPT:EE-011**

Parallel execution workflow for finrl training pipeline using the Unified Parallel Engine

## Steps

### Step 1: Setup Env
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute setup env operations for the Finrl Training Pipeline workflow.
Expected: `setup_env_artifacts`

### Step 2: Train Ppo Dqn [depends_on: setup_env]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute train ppo dqn operations for the Finrl Training Pipeline workflow.
Expected: `train_ppo_dqn_artifacts`

### Step 3: Evaluate [depends_on: train_ppo_dqn]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute evaluate operations for the Finrl Training Pipeline workflow.
Expected: `evaluate_artifacts`

### Step 4: Paper Trade [depends_on: evaluate]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute paper trade operations for the Finrl Training Pipeline workflow.
Expected: `paper_trade_artifacts`

### Step 5: Report [depends_on: paper_trade]
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute report operations for the Finrl Training Pipeline workflow.
Expected: `report_artifacts`

### Step 6: KG Persistence [depends_on: report]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Finrl Training Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Setup Env
- **After level 0:** Step 2 — Train Ppo Dqn
- **After level 1:** Step 3 — Evaluate
- **After level 2:** Step 4 — Paper Trade
- **After level 3:** Step 5 — Report
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
