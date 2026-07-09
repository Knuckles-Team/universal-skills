---
name: esg-screening-pipeline
description: >-
  Parallel execution workflow for esg screening pipeline using the Unified Parallel Engine
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
tags: [finance, esg-screening-pipeline]
concept: CONCEPT:EE-011
---

# Esg Screening Pipeline Workflow

**CONCEPT:EE-011**

Parallel execution workflow for esg screening pipeline using the Unified Parallel Engine

## Steps

### Step 1: Esg Score Lookup
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute esg score lookup operations for the Esg Screening Pipeline workflow.
Expected: `esg_score_lookup_artifacts`

### Step 2: Controversy Check [depends_on: esg_score_lookup]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute controversy check operations for the Esg Screening Pipeline workflow.
Expected: `controversy_check_artifacts`

### Step 3: Exclusion Filter [depends_on: controversy_check]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute exclusion filter operations for the Esg Screening Pipeline workflow.
Expected: `exclusion_filter_artifacts`

### Step 4: KG Persistence [depends_on: exclusion_filter]
**Agent**: `risk-assessor`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Esg Screening Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Esg Score Lookup
- **After level 0:** Step 2 — Controversy Check
- **After level 1:** Step 3 — Exclusion Filter
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
