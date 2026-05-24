---
name: portfolio_rebalance_cycle
description: Audits current portfolio position ledger weights, calculates MVO targets, sizers trades, and routes rebalances.
domain: finance
tags: [rebalance, portfolio, mvo, execution]
---
# Portfolio Rebalance Cycle Workflow

This workflow coordinates multi-agent parallel executions of Audits current portfolio position ledger weights, calculates MVO targets, sizers trades, and routes rebalances.

### Step 1: position-auditor [depends_on: none]
Fetches current exchange asset holdings and currency weights.
Expected: current-portfolio-holdings

### Step 2: mean-variance-optimizer [depends_on: position-auditor]
Runs a mean-variance and Black-Litterman allocation model.
Expected: target-portfolio-allocations

### Step 3: order-sizer-generator [depends_on: mean-variance-optimizer]
Matches target weights to calculate standard buy and sell trade size lots.
Expected: sized-rebalancing-orders

### Step 4: rebalance-executor [depends_on: order-sizer-generator]
Dispatches execution orders and verifies correct settlement feeds.
Expected: execution-rebalancing-receipts

