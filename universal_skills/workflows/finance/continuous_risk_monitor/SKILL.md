---
name: continuous_risk_monitor
description: >-
  Parallel execution workflow for continuous risk monitor using the Unified Parallel Engine
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
tags: [finance, continuous-risk-monitor]
concept: CONCEPT:EE-011
---

# Continuous Risk Monitor Workflow

**CONCEPT:EE-011**

Parallel execution workflow for continuous risk monitor using the Unified Parallel Engine

## Steps

### Step 1: Drawdown Check
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute drawdown check operations for the Continuous Risk Monitor workflow.
Expected: `drawdown_check_artifacts`

### Step 2: Daily Loss
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute daily loss operations for the Continuous Risk Monitor workflow.
Expected: `daily_loss_artifacts`

### Step 3: Regime Shift
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute regime shift operations for the Continuous Risk Monitor workflow.
Expected: `regime_shift_artifacts`

### Step 4: Position Limits
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute position limits operations for the Continuous Risk Monitor workflow.
Expected: `position_limits_artifacts`

### Step 5: Circuit Breaker [depends_on: drawdown_check, daily_loss, regime_shift, position_limits]
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute circuit breaker operations for the Continuous Risk Monitor workflow.
Expected: `circuit_breaker_artifacts`

### Step 6: KG Persistence [depends_on: circuit_breaker]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Continuous Risk Monitor results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
