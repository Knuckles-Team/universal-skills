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
  schedule: "0 9 * * 1"
  enabled: true
  timezone: "America/New_York"
  max_concurrent: 1
metadata:
  version: '1.1.0'
  author: agent-utilities
  concept: 'CONCEPT:KG-2.6'
---
# Portfolio Rebalance Workflow (Cron: Monday 9AM ET)

## Workflow Execution Steps

### Step 1: fetch-positions
Get current portfolio state from exchange.
Tool: `emerald_portfolio(action="positions")` + `emerald_portfolio(action="account")`

### Step 2: optimize
Run portfolio optimization (MVO/Risk-Parity/Black-Litterman).
Tool: Route to `data-science-mcp` for heavy optimization compute.

### Step 3: attribution
Brinson decomposition of recent performance.
Tool: Route to agent-utilities `profit_attribution.py`.

### Step 4: generate-trades
Compute rebalancing trade list from target vs current weights.

### Step 5: risk-check
Pre-trade risk validation on all rebalancing trades.
Tool: `emerald_risk(action="drawdown_check")`

### Step 6: execute
Submit rebalancing orders (paper mode default).
Tool: `emerald_orders(action="submit", ...)` for each trade.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — fetch-positions; Step 2 — optimize; Step 3 — attribution; Step 4 — generate-trades; Step 5 — risk-check; Step 6 — execute

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
