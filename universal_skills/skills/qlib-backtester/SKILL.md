---
name: qlib-backtester
domain: finance
skill_type: skill
description: Execute rigorous backtesting on alpha factors using Qlib.
metadata:
  version: '1.6.2'
---

# Qlib Backtester Skill

Use this skill to submit an `evaluate_alpha` action via `graph_analyze` or `run_qlib_backtest` via `graph_orchestrate`.

## Steps

1. Receive the hypothesis and alpha signals as an `evaluate_alpha` payload. Verify that the request names the factor expression, instrument universe and date range.
2. Formulate the Qlib dataset configuration. Verify that `python3 -c "import qlib"` succeeds and the config's start and end dates fall inside available data.
3. Submit the request via `graph_analyze` with the `evaluate_alpha` action or `graph_orchestrate` with `run_qlib_backtest`. Verify that the call returns a run id.
4. Extract `Sharpe`, `IC` and `Return` from the result. Verify that all three metrics are numeric and not NaN.
5. Write a `BacktestResult` to the KG with `graph_write(action="add_node", node_type="BacktestResult", ...)` linked to the Alpha factor. Verify with `graph_query` that the node and its link are returned.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Backtest returns empty metrics | Date range or universe has no data | Narrow the dates to the available range and resubmit |
| `import qlib` fails | Qlib is not installed on the executing node | Install `pyqlib` on the node or route the request to the data-science node |
| `BacktestResult` not linked to the factor | The factor node id was missing from the write | Look up the Alpha node id with `graph_query` and add the edge explicitly |


1. Receive hypothesis and alpha signals.
2. Formulate Qlib dataset configuration.
3. Submit backtesting request.
4. Extract performance metrics (Sharpe Ratio, IC, Return).
5. Update Knowledge Graph with `BacktestResult` connected to the Alpha factor.
