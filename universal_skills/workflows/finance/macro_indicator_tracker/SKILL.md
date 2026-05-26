---
name: macro_indicator_tracker
description: >-
  Parallel execution workflow for macro indicator tracker using the Unified Parallel Engine
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
tags: [finance, macro-indicator-tracker]
concept: CONCEPT:EE-011
---

# Macro Indicator Tracker Workflow

**CONCEPT:EE-011**

Parallel execution workflow for macro indicator tracker using the Unified Parallel Engine

## Steps

### Step 1: Gdp
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute gdp operations for the Macro Indicator Tracker workflow.
Expected: `gdp_artifacts`

### Step 2: Cpi
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute cpi operations for the Macro Indicator Tracker workflow.
Expected: `cpi_artifacts`

### Step 3: Pmi
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute pmi operations for the Macro Indicator Tracker workflow.
Expected: `pmi_artifacts`

### Step 4: Yields
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute yields operations for the Macro Indicator Tracker workflow.
Expected: `yields_artifacts`

### Step 5: Employment
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute employment operations for the Macro Indicator Tracker workflow.
Expected: `employment_artifacts`

### Step 6: Dashboard [depends_on: gdp, cpi, pmi, yields, employment]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute dashboard operations for the Macro Indicator Tracker workflow.
Expected: `dashboard_artifacts`

### Step 7: KG Persistence [depends_on: dashboard]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Macro Indicator Tracker results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
