---
name: polymarket_btc_15m_scheduler
description: Run 7-phase predicative up/down BTC trend prediction strategies on 15m
  contracts
domain: finance
tags:
- polymarket
- nautilus
- bitcoin
- prediction
requires:
- mcp_market_data
- mcp_signals
- mcp_strategy
- mcp_risk
- mcp_orders
- infrastructure-orchestrator
---

# polymarket_btc_15m_scheduler Workflow

Run 7-phase predicative up/down BTC trend prediction strategies on 15m contracts

### Step 0: mcp_market_data
Retrieve historical 15m price candles for BTC/USD
Expected: ohlcv_candles

### Step 1: mcp_signals [depends_on: Step 0]
Compute technical indicators like moving averages, variance, and z-scores
Expected: computed_signals

### Step 2: mcp_strategy [depends_on: Step 1]
Execute the 7-phase predicative up/down trend algorithm on the fused signals
Expected: up_down_prediction

### Step 3: mcp_risk [depends_on: Step 2]
Calculate optimal dynamic stop-loss and take-profit thresholds based on current volatility
Expected: validated_risk_parameters

### Step 4: mcp_orders [depends_on: Step 3]
Submit prediction bets to the corresponding 15m BTC market via CLOB limit orders
Expected: submitted_prediction_order

### Step 5: infrastructure-orchestrator [depends_on: Step 4]
Export trading metrics and runtime statistics to the centralized Redis/Grafana dashboard
Expected: exported_metrics_success
