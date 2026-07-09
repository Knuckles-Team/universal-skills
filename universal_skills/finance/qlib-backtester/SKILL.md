---
name: qlib-backtester
domain: finance
skill_type: skill
description: Execute rigorous backtesting on alpha factors using Qlib.
metadata:
  version: '1.0.2'
---

# Qlib Backtester Skill

Use this skill to submit an `evaluate_alpha` action via `graph_analyze` or `run_qlib_backtest` via `graph_orchestrate`.

## Workflow
1. Receive hypothesis and alpha signals.
2. Formulate Qlib dataset configuration.
3. Submit backtesting request.
4. Extract performance metrics (Sharpe Ratio, IC, Return).
5. Update Knowledge Graph with `BacktestResult` connected to the Alpha factor.
