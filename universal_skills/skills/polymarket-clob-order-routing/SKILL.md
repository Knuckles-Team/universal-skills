---
name: polymarket-clob-order-routing
skill_type: workflow
description: Automated Polymarket CLOB v2 order creation, signature signing, and REST
  API routing
domain: finance-workflows
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
metadata:
  version: '1.7.0'
---

# polymarket-clob-order-routing Workflow

Automated Polymarket CLOB v2 order creation, signature signing, and REST API routing

### Step 0: initialize-clob-client [skill: emerald-exchange]
Initialize CLOB Client & API credentials using EIP-712 wallet signatures
Expected: clob_client_creds

### Step 1: mcp_market_data [depends_on: Step 0]
Fetch current Polymarket order book depth and spreads
Expected: market_quote

### Step 2: mcp_orders [depends_on: Step 1]
Construct and cryptographically sign limit or market order parameters
Expected: signed_order_payload

### Step 3: submit-clob-order [skill: emerald-exchange] [depends_on: Step 2]
Submit signed order payload to the Polymarket CLOB REST endpoint
Expected: execution_result

### Step 4: mcp_portfolio [depends_on: Step 3]
Query active position ledger to verify fill status and update balances
Expected: filled_position_data

## Steps

1. Initialize the CLOB client with `emerald-exchange` using the EIP-712 wallet signature. Verify that `clob_client_creds` contains an API key and secret.
2. Fetch order book depth and spreads via `mcp_market_data`. Verify that `market_quote` shows non-empty bids and asks.
3. Build and sign the order with `mcp_orders`. Verify that `signed_order_payload` includes a signature and the intended price and size.
4. Submit the payload through `submit-clob-order` in `emerald-exchange`. Verify that `execution_result` returns an order id.
5. Query the ledger via `mcp_portfolio`. Verify that `filled_position_data` shows the expected fill status and updated balance.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Credential derivation fails | Wrong chain id or wallet key unavailable | Reload the signer key from the secret store, confirm the chain id, and rerun Step 1 |
| Submit returns invalid signature | Order fields changed after signing | Regenerate the payload with `mcp_orders` without modifying fields, then submit again |
| Order rests unfilled | Limit price away from the touch | Cancel the order and rebuild it at a price from a fresh `market_quote` |

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — initialize-clob-client
- **After level 0:** Step 1 — mcp_market_data
- **After level 1:** Step 2 — mcp_orders
- **After level 2:** Step 3 — submit-clob-order
- **After level 3:** Step 4 — mcp_portfolio

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
