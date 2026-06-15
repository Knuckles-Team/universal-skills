---
name: strategy-lifecycle
description: >-
  Master trading pipeline: Hypothesis → Debate → Backtest → Paper → Live.
  Orchestrates the full strategy lifecycle with human approval gates.
tags: [finance, trading, strategy, lifecycle]
team_config: trading_department
agent: chief_trading_officer
metadata:
  author: agent-utilities
  version: '1.0.0'
  concept: 'CONCEPT:KG-2.6'
infrastructure:
  required:
    - service: emerald-exchange
    - service: data-science-mcp
    - service: graph-os
---
# Strategy Lifecycle Workflow

> [!IMPORTANT]
> This is the master pipeline. Every strategy must pass through ALL gates before live activation.

## Workflow Execution Steps

### Step 1: hypothesis-generation
**Agent**: quant_research_analyst
Generate trading hypothesis from KG signals, market data, and research.
Tool: `emerald_signals(action="alpha", ticker=...)`

### Step 2: trading-debate
**Agent**: chief_trading_officer
Run Bull/Bear multi-round debate to vet the hypothesis.
Tool: `graph_orchestrate(action="start_debate", task=hypothesis)`

### Step 3: risk-assessment
**Agent**: risk_compliance_officer
Pre-trade risk assessment and Kelly criterion position sizing.
Tool: `emerald_risk(action="kelly", win_rate=..., win_loss_ratio=...)`

### Step 4: backtest
**Agent**: quant_research_analyst
Rigorous backtesting via data-science-mcp on GPU node.
Tool: `graph_analyze(action="evaluate_alpha", query=hypothesis)`

### Step 5: strategy-promotion
**Agent**: chief_trading_officer
Promote strategy: Draft → Backtesting → Paper → Live.
Tool: `emerald_strategy(action="promote", strategy_id=...)`

### Step 6: human-approval
**Agent**: chief_trading_officer
REQUIRED: Human approval gate for live trading activation.
Tool: `graph_orchestrate(action="request_approval", task="live_trading_activation")`

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — hypothesis-generation; Step 2 — trading-debate; Step 3 — risk-assessment; Step 4 — backtest; Step 5 — strategy-promotion; Step 6 — human-approval

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
