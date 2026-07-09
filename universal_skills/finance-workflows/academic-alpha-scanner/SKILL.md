---
name: academic-alpha-scanner
skill_type: workflow
description: >-
  Parallel execution workflow for academic alpha scanner using the Unified Parallel Engine
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
tags: [finance, academic-alpha-scanner]
concept: CONCEPT:EE-011
metadata:
  version: '1.1.0'
---

# Academic Alpha Scanner Workflow

**CONCEPT:EE-011**

Parallel execution workflow for academic alpha scanner using the Unified Parallel Engine

## Steps

### Step 1: Arxiv
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute arxiv operations for the Academic Alpha Scanner workflow.
Expected: `arxiv_artifacts`

### Step 2: Ssrn
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute ssrn operations for the Academic Alpha Scanner workflow.
Expected: `ssrn_artifacts`

### Step 3: Nber
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute nber operations for the Academic Alpha Scanner workflow.
Expected: `nber_artifacts`

### Step 4: Extract Factors [depends_on: arxiv, ssrn, nber]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute extract factors operations for the Academic Alpha Scanner workflow.
Expected: `extract_factors_artifacts`

### Step 5: Replicate [depends_on: extract_factors]
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute replicate operations for the Academic Alpha Scanner workflow.
Expected: `replicate_artifacts`

### Step 6: Backtest [depends_on: replicate]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute backtest operations for the Academic Alpha Scanner workflow.
Expected: `backtest_artifacts`

### Step 7: KG Persistence [depends_on: backtest]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Academic Alpha Scanner results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Arxiv; Step 2 — Ssrn; Step 3 — Nber
- **After level 0:** Step 4 — Extract Factors
- **After level 1:** Step 5 — Replicate
- **After level 2:** Step 6 — Backtest
- **After level 3:** Step 7 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
