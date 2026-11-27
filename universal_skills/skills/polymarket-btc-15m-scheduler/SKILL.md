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
  version: '1.7.0'
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

## Steps

1. Pull 15m BTC/USD candles via `mcp_market_data`. Verify that the `ohlcv_candles` output covers a contiguous window with no missing 15m bars.
2. Compute moving averages, variance and z-scores via `mcp_signals`. Verify that `computed_signals` contains no NaN values.
3. Run the 7-phase up/down algorithm via `mcp_strategy`. Verify that `up_down_prediction` carries a direction and a confidence value.
4. Derive stop-loss and take-profit thresholds via `mcp_risk`. Verify that `validated_risk_parameters` are positive and consistent with current volatility.
5. Submit the CLOB limit order via `mcp_orders`. Verify that `submitted_prediction_order` returns an order id and a live or filled status.
6. Export metrics through `infrastructure-orchestrator`. Verify that `exported_metrics_success` is true and the dashboard shows the new datapoint.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Candle gaps in `ohlcv_candles` | Market-data feed dropped bars or the window crossed a contract rollover | Re-request the window from `mcp_market_data` with a wider start time and abort the cycle if gaps persist |
| Order rejected by CLOB | Stale signature, insufficient balance, or price outside tick bounds | Rebuild the order with fresh parameters from Step 4 and confirm balance via `mcp_portfolio` before resubmitting |
| Metrics export fails | Redis or Grafana endpoint unreachable | Check the endpoint with `infrastructure-orchestrator` health output and re-export the cached metrics once it is back |

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — mcp_market_data
- **After level 0:** Step 1 — mcp_signals
- **After level 1:** Step 2 — mcp_strategy
- **After level 2:** Step 3 — mcp_risk
- **After level 3:** Step 4 — mcp_orders
- **After level 4:** Step 5 — infrastructure-orchestrator

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
