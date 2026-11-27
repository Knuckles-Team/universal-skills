---
name: portfolio-rebalance
domain: finance-workflows
skill_type: workflow
description: >-
  Periodic portfolio rebalancing: Optimize → Compare → Execute.
  Supports MVO, Risk Parity, and Black-Litterman optimization.
tags: [finance, portfolio, rebalance, optimization]
team_config: trading_department
agent: chief_trading_officer
cron:
  minute: "0"
  hour: "9"
  weekday: "1"
  enabled: true
  timezone: "America/New_York"
  max_concurrent: 1
metadata:
  version: '1.7.0'
  author: Knuckles-Team
  concept: 'CONCEPT:KG-2.6'
---
# Portfolio Rebalance Workflow (Cron: Monday 9AM ET)

## Workflow Execution Steps

### Step 1: fetch-positions
Get current portfolio state from exchange.
Tool: `emerald_exchange_get_positions()` + `emerald_exchange_get_account()`

### Step 2: optimize
Run portfolio optimization (MVO/Risk-Parity/Black-Litterman).
Tool: Route to `data-science-mcp` for heavy optimization compute.

### Step 3: attribution
Brinson decomposition of recent performance.
Tool: Route to meristem `profit_attribution.py`.

### Step 4: generate-trades
Compute rebalancing trade list from target vs current weights.

### Step 5: risk-check
Pre-trade risk validation on all rebalancing trades.
Tool: `emerald_risk_drawdown_check()`

### Step 6: execute
Submit rebalancing orders (paper mode default).
Tool: `emerald_orders_submit(...)` for each trade.

## Steps

1. Pull the live state with `emerald_exchange_get_positions()` and `emerald_exchange_get_account()`. Verify that positions and account equity are non-empty.
2. Optimize target weights (MVO, Risk Parity or Black-Litterman) through `data-science-mcp`. Verify that the target weights sum to 1.0.
3. Run Brinson attribution through `profit_attribution.py`. Verify that the allocation and selection effects sum to the excess return.
4. Compute the trade list from target versus current weights into `trades.json`. Verify that the post-trade weights match the targets within tolerance.
5. Validate the trades with `emerald_risk_drawdown_check()`. Verify that every trade passes the drawdown limit.
6. Submit orders using `emerald_orders_submit(...)` in paper mode. Verify that each order returns an id and status.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Optimizer fails to converge | Singular covariance matrix or too little history | Lengthen the return window or switch to Risk Parity in the `data-science-mcp` request |
| Drawdown check blocks trades | Projected drawdown exceeds the limit | Reduce trade sizes or drop the offending trades, then rerun the check |
| Order submission errors | Exchange credentials or market closed | Confirm account access with `emerald_exchange_get_account()` and resubmit when the market is open |

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — fetch-positions; Step 2 — optimize; Step 3 — attribution; Step 4 — generate-trades; Step 5 — risk-check; Step 6 — execute

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
