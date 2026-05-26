---
name: freqtrade_strategy_deploy
description: >-
  Scaffolds standard-compliant Python strategy files for Freqtrade, runs parallel hyperparameter optimizations, dry-runs them, and elevates to live webhook monitoring.
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
tags: [freqtrade, deploy, hyperopt, automation]
concept: CONCEPT:EE-011
---

# Freqtrade Strategy Deploy Workflow

**CONCEPT:EE-011**

Scaffolds standard-compliant Python strategy files for Freqtrade, runs parallel hyperparameter optimizations, dry-runs them, and elevates to live webhook monitoring.

## Steps

### Step 1: Strategy Coder
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Code a syntax-valid Freqtrade python strategy subclass.
Expected: `freqtrade-strategy-file`

### Step 2: Hyperparameter Tuner [depends_on: strategy-coder]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Run Freqtrade hyperopt parameter sweeps in parallel.
Expected: `optimized-hyperparameters`

### Step 3: Dry Run Verify [depends_on: hyperparameter-tuner]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Deploy to dry-run container stack and assert correct connection states.
Expected: `dry-run-stability-metrics`

### Step 4: Live Enable Trigger [depends_on: dry-run-verify]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Elevate to live exchange endpoints and register with Telegram webhook.
Expected: `live-deployment-logs`

### Step 5: KG Persistence [depends_on: live-enable-trigger]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Freqtrade Strategy Deploy results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
