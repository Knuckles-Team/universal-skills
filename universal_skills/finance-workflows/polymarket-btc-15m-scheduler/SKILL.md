---
name: polymarket-btc-15m-scheduler
skill_type: workflow
description: Run 7-phase predicative up/down BTC trend prediction strategies on 15m
  contracts
domain: finance-workflows
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
metadata:
  version: '1.2.0'
---

# polymarket-btc-15m-scheduler Workflow

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

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — mcp_market_data
- **After level 0:** Step 1 — mcp_signals
- **After level 1:** Step 2 — mcp_strategy
- **After level 2:** Step 3 — mcp_risk
- **After level 3:** Step 4 — mcp_orders
- **After level 4:** Step 5 — infrastructure-orchestrator

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
