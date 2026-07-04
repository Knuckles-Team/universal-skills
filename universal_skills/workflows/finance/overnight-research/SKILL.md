---
name: overnight-research
description: >-
  Unattended overnight research loop: Generate → Backtest → Debate → Report.
tags: [finance, research, overnight, automation]
team_config: trading_department
agent: quant_research_analyst
cron:
  schedule: "0 22 * * *"
  enabled: true
  timezone: "America/New_York"
  max_concurrent: 1
metadata:
  author: agent-utilities
  version: '1.0.0'
  concept: 'CONCEPT:KG-2.6'
---
# Overnight Research Workflow (Cron: 10PM ET daily)

## Workflow Execution Steps

### Step 1: hypothesis-generation
Generate N hypotheses from KG signals and market data.
Tool: `emerald_signals(action="alpha")` + KG research query.

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

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — hypothesis-generation; Step 2 — batch-backtest; Step 3 — debate-winners; Step 4 — kg-persist; Step 5 — report

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
