---
name: portfolio-rebalance-cycle
skill_type: workflow
description: >-
  Audits current portfolio position ledger weights, calculates MVO targets, sizers trades, and routes rebalances.
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
tags: [rebalance, portfolio, mvo, execution]
concept: CONCEPT:EE-011
metadata:
  version: '1.7.0'
---

# Portfolio Rebalance Cycle Workflow

**CONCEPT:EE-011**

Audits current portfolio position ledger weights, calculates MVO targets, sizers trades, and routes rebalances.

## Steps

1. Fetch current holdings and currency weights with `graph_query` and `sx_search`. Verify that `current-portfolio-holdings` weights sum to roughly 100 percent.
2. Run the mean-variance and Black-Litterman allocation with `graph_analyze`. Verify that `target-portfolio-allocations` sums to 100 percent and respects stated constraints.
3. Convert target weights to buy and sell lots with `graph_query` and `graph_analyze`. Verify that `sized-rebalancing-orders` net to the difference between current and target weights.
4. Dispatch the orders and check settlement feeds using `graph_write`. Verify that each `execution-rebalancing-receipts` entry matches a sized order.
5. Persist the results as typed nodes and edges with `graph_write`. Verify that a follow-up `graph_query` returns the new nodes linked to existing domain entities.

### Step 1: Position Auditor
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Fetches current exchange asset holdings and currency weights.
Expected: `current-portfolio-holdings`

### Step 2: Mean Variance Optimizer [depends_on: position-auditor]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Runs a mean-variance and Black-Litterman allocation model.
Expected: `target-portfolio-allocations`

### Step 3: Order Sizer Generator [depends_on: mean-variance-optimizer]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Matches target weights to calculate standard buy and sell trade size lots.
Expected: `sized-rebalancing-orders`

### Step 4: Rebalance Executor [depends_on: order-sizer-generator]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Dispatches execution orders and verifies correct settlement feeds.
Expected: `execution-rebalancing-receipts`

### Step 5: KG Persistence [depends_on: rebalance-executor]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Weights do not sum to 100 percent | Cash or a position was missing from the audit | Re-run the audit with `graph_query` including cash balances before optimizing. |
| Optimizer returns infeasible allocations | Constraints conflict with the return estimates | Relax the conflicting constraint in the `graph_analyze` inputs and record the change in the report. |
| A rebalance order fails to settle | The settlement feed rejected the lot size | Re-size that order from the latest holdings and dispatch only the failed order. |
| `graph_write` persistence is rejected | A node has no type or no link target | Re-issue `graph_write` with a typed node and an edge to an entity located first with `graph_query`. |

## Output
- Portfolio Rebalance Cycle results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Position Auditor
- **After level 0:** Step 2 — Mean Variance Optimizer
- **After level 1:** Step 3 — Order Sizer Generator
- **After level 2:** Step 4 — Rebalance Executor
- **After level 3:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
