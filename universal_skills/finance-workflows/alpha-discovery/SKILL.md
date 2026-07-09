---
name: alpha-discovery
domain: finance-workflows
skill_type: workflow
description: >-
  Automated alpha mining: Scan market data → Generate factors → Score → Fuse signals.
tags: [finance, alpha, signals, research]
team_config: trading_department
agent: quant_research_analyst
metadata:
  version: '1.0.2'
  author: agent-utilities
  concept: 'CONCEPT:KG-2.6'
---
# Alpha Discovery Workflow

## Workflow Execution Steps

### Step 1: data-ingest
Fetch market data for target universe.
Tool: `emerald_market_data(action="historical", symbol=..., period="1y")`

### Step 2: feature-engineering
Generate alpha factors with IC/IR scoring.
Tool: `emerald_signals(action="alpha", ticker=...)`

### Step 3: regime-detection
Classify current market regime (Bull/Bear/Sideways/Crisis).
Tool: `emerald_signals(action="regime", ticker=...)`

### Step 4: signal-fusion
Bayesian fusion of all signal sources.
Tool: `emerald_signals(action="fuse", ticker=...)`

### Step 5: kg-persist
Store AlphaFactor and TradingSignal nodes in KG.
Tool: `graph_write(action="add_node", node_type="AlphaFactor", ...)`

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — data-ingest; Step 2 — feature-engineering; Step 3 — regime-detection; Step 4 — signal-fusion; Step 5 — kg-persist

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
