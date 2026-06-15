---
name: dividend_reinvestment
description: >-
  Audits cash dividend payouts, fits target weight deficits, sizes reinvestment lots, and executes trades.
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
tags: [dividend, reinvestment, allocation, accounting]
concept: CONCEPT:EE-011
---

# Dividend Reinvestment Workflow

**CONCEPT:EE-011**

Audits cash dividend payouts, fits target weight deficits, sizes reinvestment lots, and executes trades.

## Steps

### Step 1: Dividend Payment Auditor
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Checks account ledger events and flags cash dividend payouts.
Expected: `dividend-ledger-receipts`

### Step 2: Target Allocation Solver [depends_on: dividend-payment-auditor]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Resolves active weights to find under-allocated target holdings.
Expected: `reinvestment-weight-adjustments`

### Step 3: Order Lot Sizing [depends_on: target-allocation-solver]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Calculates standard buy order lots matching the cash balance.
Expected: `sized-dividend-orders`

### Step 4: Reinvest Order Runner [depends_on: order-lot-sizing]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Executes trades and logs updated lot holdings parameters.
Expected: `dividend-reinvestment-logs`

### Step 5: KG Persistence [depends_on: reinvest-order-runner]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Dividend Reinvestment results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Dividend Payment Auditor
- **After level 0:** Step 2 — Target Allocation Solver
- **After level 1:** Step 3 — Order Lot Sizing
- **After level 2:** Step 4 — Reinvest Order Runner
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
