---
name: polymarket_clob_order_routing
description: Automated Polymarket CLOB v2 order creation, signature signing, and REST
  API routing
domain: finance
tags:
- polymarket
- orders
- clob
- execution
requires:
- emerald-exchange
- mcp_market_data
- mcp_orders
- mcp_portfolio
---

# polymarket_clob_order_routing Workflow

Automated Polymarket CLOB v2 order creation, signature signing, and REST API routing

### Step 0: emerald-exchange
Initialize CLOB Client & API credentials using EIP-712 wallet signatures
Expected: clob_client_creds

### Step 1: mcp_market_data [depends_on: Step 0]
Fetch current Polymarket order book depth and spreads
Expected: market_quote

### Step 2: mcp_orders [depends_on: Step 1]
Construct and cryptographically sign limit or market order parameters
Expected: signed_order_payload

### Step 3: emerald-exchange [depends_on: Step 2]
Submit signed order payload to the Polymarket CLOB REST endpoint
Expected: execution_result

### Step 4: mcp_portfolio [depends_on: Step 3]
Query active position ledger to verify fill status and update balances
Expected: filled_position_data
