---
name: regulatory_compliance_check
description: >-
  Parallel execution workflow for regulatory compliance check using the Unified Parallel Engine
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
tags: [finance, regulatory-compliance-check]
concept: CONCEPT:EE-011
---

# Regulatory Compliance Check Workflow

**CONCEPT:EE-011**

Parallel execution workflow for regulatory compliance check using the Unified Parallel Engine

## Steps

### Step 1: Position Limits
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute position limits operations for the Regulatory Compliance Check workflow.
Expected: `position_limits_artifacts`

### Step 2: Wash Sale
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute wash sale operations for the Regulatory Compliance Check workflow.
Expected: `wash_sale_artifacts`

### Step 3: Pattern Day Trader
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute pattern day trader operations for the Regulatory Compliance Check workflow.
Expected: `pattern_day_trader_artifacts`

### Step 4: Report [depends_on: position_limits, wash_sale, pattern_day_trader]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute report operations for the Regulatory Compliance Check workflow.
Expected: `report_artifacts`

### Step 5: KG Persistence [depends_on: report]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Regulatory Compliance Check results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
