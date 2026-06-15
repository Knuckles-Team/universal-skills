---
name: earnings_calendar_pipeline
description: >-
  Parallel execution workflow for earnings calendar pipeline using the Unified Parallel Engine
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
tags: [finance, earnings-calendar-pipeline]
concept: CONCEPT:EE-011
---

# Earnings Calendar Pipeline Workflow

**CONCEPT:EE-011**

Parallel execution workflow for earnings calendar pipeline using the Unified Parallel Engine

## Steps

### Step 1: Fetch Calendar
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute fetch calendar operations for the Earnings Calendar Pipeline workflow.
Expected: `fetch_calendar_artifacts`

### Step 2: Pre Earnings Analysis [depends_on: fetch_calendar]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute pre earnings analysis operations for the Earnings Calendar Pipeline workflow.
Expected: `pre_earnings_analysis_artifacts`

### Step 3: Position [depends_on: pre_earnings_analysis]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute position operations for the Earnings Calendar Pipeline workflow.
Expected: `position_artifacts`

### Step 4: Post Earnings Review [depends_on: position]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute post earnings review operations for the Earnings Calendar Pipeline workflow.
Expected: `post_earnings_review_artifacts`

### Step 5: KG Persistence [depends_on: post_earnings_review]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Earnings Calendar Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fetch Calendar
- **After level 0:** Step 2 — Pre Earnings Analysis
- **After level 1:** Step 3 — Position
- **After level 2:** Step 4 — Post Earnings Review
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
