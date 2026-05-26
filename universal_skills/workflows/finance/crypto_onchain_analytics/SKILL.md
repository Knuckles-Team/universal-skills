---
name: crypto_onchain_analytics
description: >-
  Parallel execution workflow for crypto onchain analytics using the Unified Parallel Engine
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
tags: [finance, crypto-onchain-analytics]
concept: CONCEPT:EE-011
---

# Crypto Onchain Analytics Workflow

**CONCEPT:EE-011**

Parallel execution workflow for crypto onchain analytics using the Unified Parallel Engine

## Steps

### Step 1: Whale Wallets
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute whale wallets operations for the Crypto Onchain Analytics workflow.
Expected: `whale_wallets_artifacts`

### Step 2: Exchange Flows
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute exchange flows operations for the Crypto Onchain Analytics workflow.
Expected: `exchange_flows_artifacts`

### Step 3: Dex Volume
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute dex volume operations for the Crypto Onchain Analytics workflow.
Expected: `dex_volume_artifacts`

### Step 4: Staking
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute staking operations for the Crypto Onchain Analytics workflow.
Expected: `staking_artifacts`

### Step 5: Signals [depends_on: whale_wallets, exchange_flows, dex_volume, staking]
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute signals operations for the Crypto Onchain Analytics workflow.
Expected: `signals_artifacts`

### Step 6: KG Persistence [depends_on: signals]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Crypto Onchain Analytics results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
