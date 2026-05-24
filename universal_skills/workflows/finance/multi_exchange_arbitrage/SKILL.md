---
name: multi_exchange_arbitrage
description: Scans feeds across spot and derivative exchanges concurrently, computes fee-adjusted spread funding margins, and executes both legs.
domain: finance
tags: [arbitrage, multi-exchange, derivatives, spot]
---
# Multi Exchange Arbitrage Workflow

This workflow coordinates multi-agent parallel executions of Scans feeds across spot and derivative exchanges concurrently, computes fee-adjusted spread funding margins, and executes both legs.

### Step 1: ticker-scanner [depends_on: none]
Pull price feeds across multiple spot and derivative exchange endpoints concurrently.
Expected: real-time-ticker-feeds

### Step 2: spread-analyzer [depends_on: ticker-scanner]
Calculate transaction-fee adjusted funding and spot-futures spreads in real time.
Expected: arbitrage-spread-metrics

### Step 3: order-executor [depends_on: spread-analyzer]
Simultaneously routes buy and sell legs to the respective exchanges.
Expected: order-execution-status

### Step 4: pnl-settler [depends_on: order-executor]
Audits trade fills, records ledger transaction records, and calculates net PnL.
Expected: settlement-ledger-entries

