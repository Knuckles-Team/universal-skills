---
name: dividend-reinvestment
skill_type: workflow
description: >-
  Audits cash dividend payouts, fits target weight deficits, sizes reinvestment lots, and executes trades.
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
    - report-generator
  tool_assignments:
    data-fetcher: [graph_query, sx_search]
    compute-engine: [graph_analyze]
    risk-assessor: [graph_query, graph_analyze]
    report-generator: [graph_write, document_tools]
tags: [dividend, reinvestment, allocation, accounting]
concept: CONCEPT:EE-011
metadata:
  version: '1.7.0'
---

# Dividend Reinvestment Workflow

**CONCEPT:EE-011**

Audits cash dividend payouts, fits target weight deficits, sizes reinvestment lots, and executes trades.

## Steps

1. Audit dividend receipts with the `data-fetcher` agent using `graph_query` and `sx_search`. Verify that `dividend-ledger-receipts` lists at least one cash dividend payout with an amount and date.
2. Solve target weights with the `compute-engine` agent using `graph_analyze`. Verify that `reinvestment-weight-adjustments` names each under-allocated holding with its weight deficit.
3. Size buy lots with the `risk-assessor` agent using `graph_query` and `graph_analyze`. Verify that the total cost in `sized-dividend-orders` does not exceed the dividend cash balance.
4. Execute the trades with the `report-generator` agent using `graph_write` and `document_tools`. Verify that `dividend-reinvestment-logs` records each order with updated lot holdings.
5. Persist results to the Knowledge Graph with `graph_write`. Verify that a `graph_query` for the new typed nodes returns the reinvestment records linked to their domain entities.

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

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| No dividend receipts found | Ledger events missing for the period or wrong account queried | Re-run `graph_query` with the correct account and date range, and stop the workflow if no payout exists. |
| Sized orders exceed available cash | Lot sizing used stale prices | Re-run the order lot sizing step with fresh quotes from `sx_search` before any trade is executed. |
| Trade execution fails | Broker or exchange endpoint rejected the order | Read the error in `dividend-reinvestment-logs`, correct the order parameters and re-submit only the failed lots. |

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

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
