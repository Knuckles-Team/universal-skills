---
name: tax-lot-optimization
skill_type: workflow
description: >-
  Parses lot ledger dates, computes unrealized holding gains, harvests short/long term losses, and synthesizes lot trades.
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
tags: [tax-harvest, lot-ledger, unrealized-gains, accounting]
concept: CONCEPT:EE-011
metadata:
  version: '1.7.0'
---

# Tax Lot Optimization Workflow

**CONCEPT:EE-011**

Parses lot ledger dates, computes unrealized holding gains, harvests short/long term losses, and synthesizes lot trades.

## Steps

1. Parse the lot ledger with `graph_query` and `sx_search`. Verify that `tax-lot-inventories` lists acquisition dates and cost basis for every lot.
2. Compute unrealized gains with `graph_analyze`. Verify that `unrealized-capital-gains` separates short-term and long-term totals.
3. Select harvest candidates under MinTax or FIFO with `graph_query` and `graph_analyze`. Verify that `harvest-lot-candidates` names the policy used.
4. Synthesize order proposals with `graph_write` and `document_tools`. Verify that `tax-optimized-order-proposals` references only lots from the inventory.
5. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

### Step 1: Lot Ledger Parser
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Standardizes transaction acquisition date records and cost basis parameters.
Expected: `tax-lot-inventories`

### Step 2: Unrealized Gain Calculator [depends_on: lot-ledger-parser]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Measures unrealized short-term and long-term gains and losses.
Expected: `unrealized-capital-gains`

### Step 3: Harvest Candidate Selector [depends_on: unrealized-gain-calculator]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Identifies tax-loss harvesting candidates using MinTax/FIFO policies.
Expected: `harvest-lot-candidates`

### Step 4: Order Proposal Synthesis [depends_on: harvest-candidate-selector]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Synthesizes optimized lot execution recommendations.
Expected: `tax-optimized-order-proposals`

### Step 5: KG Persistence [depends_on: order-proposal-synthesis]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Lots lack acquisition dates | Ledger export is incomplete | Re-export the ledger with dates and cost basis and re-run the parse step. |
| Gains do not reconcile | Price data is stale | Refresh prices and recompute with `graph_analyze`. |
| No candidates found | No lots with losses | Report that no harvest is available and skip order synthesis. |

## Output
- Tax Lot Optimization results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Lot Ledger Parser
- **After level 0:** Step 2 — Unrealized Gain Calculator
- **After level 1:** Step 3 — Harvest Candidate Selector
- **After level 2:** Step 4 — Order Proposal Synthesis
- **After level 3:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
