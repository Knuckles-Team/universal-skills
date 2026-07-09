---
name: polymarket-liquidity-mm
skill_type: workflow
description: Dual-sided market making with automated inventory skew balancing and
  capital recycling via position merging
domain: finance-workflows
tags:
- polymarket
- market-making
- inventory-skew
- merger
requires:
- mcp_market_data
- mcp_portfolio
- mcp_risk
- mcp_orders
metadata:
  version: '1.2.0'
---

# polymarket-liquidity-mm Workflow

Dual-sided market making with automated inventory skew balancing and capital recycling via position merging

### Step 0: mcp_market_data
Monitor target market orderbook depth and calculate best bid/ask spreads
Expected: bid_ask_depth

### Step 1: mcp_portfolio [depends_on: Step 0]
Analyze active token inventory and portfolio balance ratio
Expected: inventory_weight

### Step 2: mcp_risk [depends_on: Step 1]
Compute inventory skew quoting offsets (lower ask if long, higher bid if short)
Expected: quoting_price_offsets

### Step 3: mcp_orders [depends_on: Step 2]
Place dual-sided limit orders on target market to capture spread
Expected: dual_limit_orders

### Step 4: mcp_orders [depends_on: Step 3]
Cancel stale or out-of-range quotes and dynamically adjust offsets based on volatility
Expected: updated_market_making_state

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — mcp_market_data
- **After level 0:** Step 1 — mcp_portfolio
- **After level 1:** Step 2 — mcp_risk
- **After level 2:** Step 3 — mcp_orders
- **After level 3:** Step 4 — mcp_orders

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
