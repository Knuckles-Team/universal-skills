---
name: dividend_reinvestment
description: Audits cash dividend payouts, fits target weight deficits, sizes reinvestment lots, and executes trades.
domain: finance
tags: [dividend, reinvestment, allocation, accounting]
---
# Dividend Reinvestment Workflow

This workflow coordinates multi-agent parallel executions of Audits cash dividend payouts, fits target weight deficits, sizes reinvestment lots, and executes trades.

### Step 1: dividend-payment-auditor [depends_on: none]
Checks account ledger events and flags cash dividend payouts.
Expected: dividend-ledger-receipts

### Step 2: target-allocation-solver [depends_on: dividend-payment-auditor]
Resolves active weights to find under-allocated target holdings.
Expected: reinvestment-weight-adjustments

### Step 3: order-lot-sizing [depends_on: target-allocation-solver]
Calculates standard buy order lots matching the cash balance.
Expected: sized-dividend-orders

### Step 4: reinvest-order-runner [depends_on: order-lot-sizing]
Executes trades and logs updated lot holdings parameters.
Expected: dividend-reinvestment-logs

