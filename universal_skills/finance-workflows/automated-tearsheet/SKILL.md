---
name: automated-tearsheet
skill_type: workflow
description: >-
  Parallel execution workflow for automated tearsheet using the Unified Parallel Engine
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
tags: [finance, automated-tearsheet]
concept: CONCEPT:EE-011
metadata:
  version: '1.1.0'
---

# Automated Tearsheet Workflow

**CONCEPT:EE-011**

Parallel execution workflow for automated tearsheet using the Unified Parallel Engine

## Steps

### Step 1: Pull Performance
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute pull performance operations for the Automated Tearsheet workflow.
Expected: `pull_performance_artifacts`

### Step 2: Calc Metrics [depends_on: pull_performance]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute calc metrics operations for the Automated Tearsheet workflow.
Expected: `calc_metrics_artifacts`

### Step 3: Generate Charts [depends_on: calc_metrics]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute generate charts operations for the Automated Tearsheet workflow.
Expected: `generate_charts_artifacts`

### Step 4: Email Report [depends_on: generate_charts]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute email report operations for the Automated Tearsheet workflow.
Expected: `email_report_artifacts`

### Step 5: KG Persistence [depends_on: email_report]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Automated Tearsheet results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Pull Performance
- **After level 0:** Step 2 — Calc Metrics
- **After level 1:** Step 3 — Generate Charts
- **After level 2:** Step 4 — Email Report
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
