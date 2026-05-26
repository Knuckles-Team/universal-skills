---
name: exchange_health_monitor
description: >-
  Parallel execution workflow for exchange health monitor using the Unified Parallel Engine
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
tags: [finance, exchange-health-monitor]
concept: CONCEPT:EE-011
---

# Exchange Health Monitor Workflow

**CONCEPT:EE-011**

Parallel execution workflow for exchange health monitor using the Unified Parallel Engine

## Steps

### Step 1: Prerequisites Setup
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute prerequisites setup operations for the Exchange Health Monitor workflow.
Expected: `prerequisites_setup_artifacts`

### Step 2: Parallel Execution [depends_on: prerequisites_setup]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute parallel execution operations for the Exchange Health Monitor workflow.
Expected: `parallel_execution_artifacts`

### Step 3: Verification And Testing [depends_on: parallel_execution]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute verification and testing operations for the Exchange Health Monitor workflow.
Expected: `verification_and_testing_artifacts`

### Step 4: Synthesis And Reporting [depends_on: verification_and_testing]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute synthesis and reporting operations for the Exchange Health Monitor workflow.
Expected: `synthesis_and_reporting_artifacts`

### Step 5: KG Persistence [depends_on: synthesis_and_reporting]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Exchange Health Monitor results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
