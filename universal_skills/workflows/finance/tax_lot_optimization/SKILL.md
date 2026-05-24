---
name: tax_lot_optimization
description: Parses lot ledger dates, computes unrealized holding gains, harvests short/long term losses, and synthesizes lot trades.
domain: finance
tags: [tax-harvest, lot-ledger, unrealized-gains, accounting]
---
# Tax Lot Optimization Workflow

This workflow coordinates multi-agent parallel executions of Parses lot ledger dates, computes unrealized holding gains, harvests short/long term losses, and synthesizes lot trades.

### Step 1: lot-ledger-parser [depends_on: none]
Standardizes transaction acquisition date records and cost basis parameters.
Expected: tax-lot-inventories

### Step 2: unrealized-gain-calculator [depends_on: lot-ledger-parser]
Measures unrealized short-term and long-term gains and losses.
Expected: unrealized-capital-gains

### Step 3: harvest-candidate-selector [depends_on: unrealized-gain-calculator]
Identifies tax-loss harvesting candidates using MinTax/FIFO policies.
Expected: harvest-lot-candidates

### Step 4: order-proposal-synthesis [depends_on: harvest-candidate-selector]
Synthesizes optimized lot execution recommendations.
Expected: tax-optimized-order-proposals

