---
name: polymarket_liquidity_mm
description: Dual-sided market making with automated inventory skew balancing and
  capital recycling via position merging
domain: finance
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
---

# polymarket_liquidity_mm Workflow

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
