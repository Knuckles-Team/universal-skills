---
name: strategy-lifecycle
domain: finance-workflows
skill_type: workflow
description: >-
  Master trading pipeline: Hypothesis → Debate → Backtest → Paper → Live.
  Orchestrates the full strategy lifecycle with human approval gates.
tags: [finance, trading, strategy, lifecycle]
team_config: trading_department
agent: chief_trading_officer
metadata:
  version: '1.6.2'
  author: Knuckles-Team
  concept: 'CONCEPT:KG-2.6'
infrastructure:
  required:
    - service: emerald-exchange
    - service: data-science-mcp
    - service: arbora
---
# Strategy Lifecycle Workflow

> [!IMPORTANT]
> This is the master pipeline. Every strategy must pass through ALL gates before live activation.

## Workflow Execution Steps

### Step 1: hypothesis-generation
**Agent**: quant_research_analyst
Generate trading hypothesis from KG signals, market data, and research.
Tool: `emerald_signals_alpha(ticker=...)`

### Step 2: trading-debate
**Agent**: chief_trading_officer
Run Bull/Bear multi-round debate to vet the hypothesis.
Tool: `graph_orchestrate(action="start_debate", task=hypothesis)`

### Step 3: risk-assessment
**Agent**: risk_compliance_officer
Pre-trade risk assessment and Kelly criterion position sizing.
Tool: `emerald_risk_kelly(win_rate=..., win_loss_ratio=...)`

### Step 4: backtest
**Agent**: quant_research_analyst
Rigorous backtesting via data-science-mcp on GPU node.
Tool: `graph_analyze(action="evaluate_alpha", query=hypothesis)`

### Step 5: strategy-promotion
**Agent**: chief_trading_officer
Promote strategy: Draft → Backtesting → Paper → Live.
Tool: `emerald_strategy_promote(strategy_id=...)`

### Step 6: human-approval
**Agent**: chief_trading_officer
REQUIRED: Human approval gate for live trading activation.
Tool: `graph_orchestrate(action="request_approval", task="live_trading_activation")`

## Steps

1. Generate the hypothesis with `emerald_signals_alpha(ticker=...)`. Verify that the result names a ticker, a signal and supporting data before moving on.
2. Debate it with `graph_orchestrate(action="start_debate", task=hypothesis)`. Verify that the response contains Bull and Bear rounds and a consensus outcome.
3. Size the position with `emerald_risk_kelly(win_rate=..., win_loss_ratio=...)`. Verify that the returned fraction is positive and within the risk officer's limit.
4. Backtest with `graph_analyze(action="evaluate_alpha", query=hypothesis)`. Verify that the result reports return and drawdown metrics for the tested period.
5. Promote the strategy with `emerald_strategy_promote(strategy_id=...)`. Verify that the returned status advanced exactly one stage (Draft, Backtesting, Paper or Live).
6. Request live approval with `graph_orchestrate(action="request_approval", task="live_trading_activation")`. Verify that a human approval is recorded before any live activation.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Debate ends without consensus | Risk veto or conflicting Bull/Bear outcome | Stop the pipeline, revise the hypothesis, and rerun the debate step with the revised task text |
| Kelly fraction is zero or negative | Win rate and win/loss ratio imply no edge | Do not promote; return to hypothesis generation with new inputs |
| `emerald_strategy_promote` rejects the stage | Required prior stage evidence is missing (for example no backtest) | Complete the backtest step and resubmit the promotion for the same `strategy_id` |
| Approval request is not granted | No human decision recorded | Leave the strategy in Paper and ask the owner to decide through the approval request; never activate live without it |

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — hypothesis-generation; Step 2 — trading-debate; Step 3 — risk-assessment; Step 4 — backtest; Step 5 — strategy-promotion; Step 6 — human-approval

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
