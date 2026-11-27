---
name: overnight-research
domain: finance-workflows
skill_type: workflow
description: >-
  Unattended overnight research loop: Generate → Backtest → Debate → Report.
tags: [finance, research, overnight, automation]
team_config: trading_department
agent: quant_research_analyst
cron:
  minute: "0"
  hour: "22"
  enabled: true
  timezone: "America/New_York"
  max_concurrent: 1
metadata:
  version: '1.7.0'
  author: Knuckles-Team
  concept: 'CONCEPT:KG-2.6'
---
# Overnight Research Workflow (Cron: 10PM ET daily)

## Workflow Execution Steps

### Step 1: hypothesis-generation
Generate N hypotheses from KG signals and market data.
Tool: `emerald_signals_alpha()` + KG research query.

### Step 2: batch-backtest
Run all hypotheses through qlib backtest queue on GPU node.
Tool: Route to `data-science-mcp` for batch execution.

### Step 3: debate-winners
Debate top-performing hypotheses via trading swarm.
Tool: `graph_orchestrate(action="start_debate", task=top_hypothesis)`

### Step 4: kg-persist
Store validated strategies and research results in KG.
Tool: `graph_write(action="add_node", node_type="BacktestResult", ...)`

### Step 5: report
Generate research report with rankings and recommendations.

## Steps

1. Generate the hypotheses from KG signals by calling `emerald_signals_alpha()` plus a KG research query. Verify that the result holds at least one hypothesis with a name and signal definition before continuing.
2. Backtest every hypothesis by routing the batch to `data-science-mcp`. Verify that each hypothesis has a returned metrics record (Sharpe, return) and none are left queued.
3. Debate the top performers with `graph_orchestrate(action="start_debate", task=top_hypothesis)`. Verify that the debate output names a keep or reject verdict per hypothesis.
4. Persist the validated strategies with `graph_write(action="add_node", node_type="BacktestResult", ...)`. Verify that a `graph_query` for `BacktestResult` nodes returns the new entries.
5. Write the ranked research report with recommendations. Verify that every persisted `BacktestResult` appears in the report's ranking table.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Backtest queue never returns | GPU node or `data-science-mcp` is unreachable | Check the MCP server health, restart the backtest batch on the CPU fallback node, and rerun Step 2 only for hypotheses without results |
| Debate returns no verdict | `graph_orchestrate` start_debate lacked the top hypothesis payload | Resubmit with `task` set to the ranked top hypothesis text from Step 2 output |
| `BacktestResult` write rejected | Node properties missing required fields or arbora unreachable | Inspect the error, add the missing properties, and rewrite the node; fall back to native step execution if arbora is down |
| Cron run overlaps previous night | `max_concurrent` is 1 and the prior run is still active | Inspect the running workflow and cancel or wait for it, then let the next scheduled run proceed |

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — hypothesis-generation; Step 2 — batch-backtest; Step 3 — debate-winners; Step 4 — kg-persist; Step 5 — report

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
