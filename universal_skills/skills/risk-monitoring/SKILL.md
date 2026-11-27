---
name: risk-monitoring
domain: finance-workflows
skill_type: workflow
description: >-
  Continuous risk surveillance on cron schedule.
  Checks drawdown, daily loss, regime shifts, and circuit breakers.
tags: [finance, risk, monitoring, cron]
team_config: trading_department
agent: risk_compliance_officer
cron:
  minute: "0,5,10,15,20,25,30,35,40,45,50,55"
  enabled: true
  timezone: "America/New_York"
  max_concurrent: 1
metadata:
  version: '1.7.0'
  author: Knuckles-Team
  concept: 'CONCEPT:EE-011'
---
# Risk Monitoring Workflow (Cron: every 5 minutes)

## Steps

1. Pull open positions with `emerald_exchange_get_positions()`. Verify that the call returns a position list (empty is valid) and not an error payload.
2. Evaluate limits with `emerald_risk_drawdown_check()` and `emerald_risk_daily_loss_check(daily_pnl=...)`. Verify that both return a numeric risk score that you record.
3. Check for regime shifts with `emerald_signals_regime()`. Verify that the response carries the KS-test result and a timestamp.
4. Halt trading with `emerald_orders_halt()` only when any score is at or above 1.0. Verify that a halt call is followed by a position or order status read showing trading halted.
5. Persist the snapshot with `graph_write(action="add_node", node_type="RiskSnapshot", ...)`. Verify that `graph_query` for `MATCH (r:RiskSnapshot) RETURN r ORDER BY r.timestamp DESC LIMIT 1` returns the new node.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `emerald_exchange_get_positions` errors | The exchange backend is unreachable or credentials expired | Treat the cycle as unverified, do not report a clean snapshot, and alert the `risk_compliance_officer` agent to restore the backend |
| A check returns a score of 1.0 or more | A drawdown, daily-loss or regime threshold is breached | Call `emerald_orders_halt()` immediately, then persist the snapshot with the breach flagged |
| `graph_write` fails to store the snapshot | The KG is unreachable | Keep the metrics in the run output, and write the missing `RiskSnapshot` once `graph_query` answers again |
| Two runs overlap | A cycle exceeded the 5-minute cron interval | Rely on `max_concurrent: 1` and investigate the slow tool call from its timing in the run trace |

## Workflow Execution Steps

### Step 1: portfolio-scan
Query active positions from exchange backend.
Tool: `emerald_exchange_get_positions()`

### Step 2: drawdown-check
Check portfolio drawdown against configured limits.
Tool: `emerald_risk_drawdown_check()`

### Step 3: daily-loss-check
Check daily P&L against loss limits.
Tool: `emerald_risk_daily_loss_check(daily_pnl=...)`

### Step 4: regime-check
Check for regime shifts using KS-test.
Tool: `emerald_signals_regime()`

### Step 5: circuit-breaker
If ANY threshold is breached, halt trading immediately.
Tool: `emerald_orders_halt()` if risk score >= 1.0

### Step 6: kg-persist
Store RiskSnapshot node in KG with timestamp and metrics.
Tool: `graph_write(action="add_node", node_type="RiskSnapshot", ...)`

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — portfolio-scan; Step 2 — drawdown-check; Step 3 — daily-loss-check; Step 4 — regime-check; Step 5 — circuit-breaker; Step 6 — kg-persist

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
