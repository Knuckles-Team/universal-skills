---
name: market_microstructure_analysis
description: Audits millisecond order book snapshot logs, computes VPIN metrics, decomposes spreads, and aggregates impact reports.
domain: finance
tags: [microstructure, order-book, vpin, slippage]
---
# Market Microstructure Analysis Workflow

This workflow coordinates multi-agent parallel executions of Audits millisecond order book snapshot logs, computes VPIN metrics, decomposes spreads, and aggregates impact reports.

### Step 1: book-snapshot-crawlers [depends_on: none]
Collects millisecond order book snapshot logs.
Expected: order-book-snapshots

### Step 2: flow-toxicity-calculator [depends_on: book-snapshot-crawlers]
Calculates VPIN and buy-sell order flow imbalance.
Expected: volume-toxicity-signals

### Step 3: spread-decomposition [depends_on: flow-toxicity-calculator]
Decomposes bid-ask spread into inventory and adverse selection.
Expected: decomposed-spread-metrics

### Step 4: impact-report [depends_on: spread-decomposition]
Compiles execution cost optimization recommendation cards.
Expected: microstructure-impact-tearsheet

