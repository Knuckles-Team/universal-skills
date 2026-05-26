---
name: trade_journal_analysis
description: >-
  Parallel execution workflow for trade journal analysis using the Unified Parallel Engine
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
tags: [finance, trade-journal-analysis]
concept: CONCEPT:EE-011
---

# Trade Journal Analysis Workflow

**CONCEPT:EE-011**

Parallel execution workflow for trade journal analysis using the Unified Parallel Engine

## Steps

### Step 1: Pull Trade Log
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute pull trade log operations for the Trade Journal Analysis workflow.
Expected: `pull_trade_log_artifacts`

### Step 2: Classify Decisions [depends_on: pull_trade_log]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute classify decisions operations for the Trade Journal Analysis workflow.
Expected: `classify_decisions_artifacts`

### Step 3: Ev Analysis [depends_on: classify_decisions]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute ev analysis operations for the Trade Journal Analysis workflow.
Expected: `ev_analysis_artifacts`

### Step 4: Parameter Update [depends_on: ev_analysis]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute parameter update operations for the Trade Journal Analysis workflow.
Expected: `parameter_update_artifacts`

### Step 5: KG Persistence [depends_on: parameter_update]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Trade Journal Analysis results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
