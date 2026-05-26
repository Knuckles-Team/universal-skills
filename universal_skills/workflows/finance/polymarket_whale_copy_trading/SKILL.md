---
name: polymarket_whale_copy_trading
description: Mirror leaderboard whale wallet trades in real-time syncing activity
  to a local database ledger
domain: finance
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
---

# polymarket_whale_copy_trading Workflow

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
