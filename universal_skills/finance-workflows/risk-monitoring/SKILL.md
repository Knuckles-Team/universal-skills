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
  schedule: "*/5 * * * *"
  enabled: true
  timezone: "America/New_York"
  max_concurrent: 1
metadata:
  version: '1.0.2'
  author: agent-utilities
  concept: 'CONCEPT:EE-011'
---
# Risk Monitoring Workflow (Cron: every 5 minutes)

## Workflow Execution Steps

### Step 1: portfolio-scan
Query active positions from exchange backend.
Tool: `emerald_portfolio(action="positions")`

### Step 2: drawdown-check
Check portfolio drawdown against configured limits.
Tool: `emerald_risk(action="drawdown_check")`

### Step 3: daily-loss-check
Check daily P&L against loss limits.
Tool: `emerald_risk(action="daily_loss_check", daily_pnl=...)`

### Step 4: regime-check
Check for regime shifts using KS-test.
Tool: `emerald_signals(action="regime")`

### Step 5: circuit-breaker
If ANY threshold is breached, halt trading immediately.
Tool: `emerald_orders(action="halt")` if risk score >= 1.0

### Step 6: kg-persist
Store RiskSnapshot node in KG with timestamp and metrics.
Tool: `graph_write(action="add_node", node_type="RiskSnapshot", ...)`

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — portfolio-scan; Step 2 — drawdown-check; Step 3 — daily-loss-check; Step 4 — regime-check; Step 5 — circuit-breaker; Step 6 — kg-persist

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
