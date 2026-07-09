---
name: polymarket-multi-strategy-arb
description: Execute multiple Polymarket prediction strategies covering arbitrage,
  news sentiment, and traditional odds differences
domain: finance
tags:
- polymarket
- arbitrage
- sentiment
- odds-tracking
requires:
- web-search
- mcp_market_data
- mcp_signals
- mcp_strategy
- mcp_orders
---

# polymarket-multi-strategy-arb Workflow

Execute multiple Polymarket prediction strategies covering arbitrage, news sentiment, and traditional odds differences

### Step 0: mcp_market_data
Fetch current contract odds from target Polymarket outcome market
Expected: contract_odds

### Step 1: web-search [depends_on: Step 0]
Scrape and analyze news and social sentiment signals for prediction probability
Expected: sentiment_score

### Step 2: mcp_signals [depends_on: Step 0]
Retrieve pricing data from external prediction markets and traditional sportsbooks
Expected: external_market_odds

### Step 3: mcp_strategy [depends_on: Step 1, Step 2]
Compare prices across platforms to identify positive expected value (+EV) arbitrage opportunities
Expected: selected_arbitrage_target

### Step 4: mcp_orders [depends_on: Step 3]
Route execution orders to capture the pricing discrepancy
Expected: arbitrage_execution_result

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — mcp_market_data
- **After level 0:** Step 1 — web-search; Step 2 — mcp_signals
- **After level 1:** Step 3 — mcp_strategy
- **After level 2:** Step 4 — mcp_orders

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
