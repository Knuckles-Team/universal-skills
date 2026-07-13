---
name: portfolio-analysis
skill_type: workflow
description: >-
  Parallel execution workflow for portfolio analysis using the Unified Parallel Engine
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
  tool_assignments:
    data-fetcher: [graph_query, sx_search]
    compute-engine: [graph_analyze]
    risk-assessor: [graph_query, graph_analyze]
tags: [finance, analysis, portfolio]
concept: CONCEPT:EE-011
metadata:
  version: '1.2.1'
---

# Portfolio Analysis Workflow

**CONCEPT:EE-011**

>-

## Steps

### Step 1: Data Extractor
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Extract the latest holding data from the portfolio system and fetch benchmark data.

### Step 2: Risk Analyzer
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Calculate risk metrics, exposures, and VaR based on the extracted holding data.

### Step 3: Report Generator
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Synthesize the risk metrics and holding data into a formatted markdown report.

### Step 4: KG Persistence [depends_on: report-generator]
**Agent**: `risk-assessor`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Portfolio Analysis results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Data Extractor; Step 2 — Risk Analyzer; Step 3 — Report Generator
- **After level 0:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
