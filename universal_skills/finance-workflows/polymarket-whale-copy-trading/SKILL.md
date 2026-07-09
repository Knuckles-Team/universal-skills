---
name: polymarket-whale-copy-trading
skill_type: workflow
description: Mirror leaderboard whale wallet trades in real-time syncing activity
  to a local database ledger
domain: finance-workflows
tags:
- polymarket
- copy-trading
- whale-tracking
- supabase
requires:
- database-tools
- mcp_signals
- mcp_risk
- mcp_orders
metadata:
  version: '1.0.2'
---

# polymarket-whale-copy-trading Workflow

Mirror leaderboard whale wallet trades in real-time syncing activity to a local database ledger

### Step 0: mcp_signals
Poll target top-performing Polymarket trader wallet addresses
Expected: whale_trade_event

### Step 1: database-tools [depends_on: Step 0]
Sync detected whale trade activity to local Supabase database to avoid duplication
Expected: synced_database_record

### Step 2: mcp_risk [depends_on: Step 1]
Validate copy trades against local balance constraints and capital allocation percentages
Expected: validated_trade_sizing

### Step 3: mcp_orders [depends_on: Step 2]
Mirror the target trade by placing corresponding buy/sell orders via the CLOB client
Expected: submitted_copy_order

### Step 4: database-tools [depends_on: Step 3]
Update Supabase historical trade ledger with local execution prices and order status
Expected: updated_ledger_record

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — mcp_signals
- **After level 0:** Step 1 — database-tools
- **After level 1:** Step 2 — mcp_risk
- **After level 2:** Step 3 — mcp_orders
- **After level 3:** Step 4 — database-tools

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
