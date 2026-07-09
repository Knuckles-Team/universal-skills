---
name: liquidity_risk_assessment
description: >-
  Parallel execution workflow for liquidity risk assessment using the Unified Parallel Engine
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
tags: [finance, liquidity-risk-assessment]
concept: CONCEPT:EE-011
---

# Liquidity Risk Assessment Workflow

**CONCEPT:EE-011**

Parallel execution workflow for liquidity risk assessment using the Unified Parallel Engine

## Steps

### Step 1: Volume Profile
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute volume profile operations for the Liquidity Risk Assessment workflow.
Expected: `volume_profile_artifacts`

### Step 2: Bid Ask Spread
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute bid ask spread operations for the Liquidity Risk Assessment workflow.
Expected: `bid_ask_spread_artifacts`

### Step 3: Market Impact
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute market impact operations for the Liquidity Risk Assessment workflow.
Expected: `market_impact_artifacts`

### Step 4: Score [depends_on: volume_profile, bid_ask_spread, market_impact]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute score operations for the Liquidity Risk Assessment workflow.
Expected: `score_artifacts`

### Step 5: KG Persistence [depends_on: score]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Liquidity Risk Assessment results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Volume Profile; Step 2 — Bid Ask Spread; Step 3 — Market Impact
- **After level 0:** Step 4 — Score
- **After level 1:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
