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
  version: '1.6.2'
  author: Knuckles-Team
  concept: 'CONCEPT:KG-2.6'
---
# Alpha Discovery Workflow

## Workflow Execution Steps

### Step 1: data-ingest
Fetch market data for target universe.
Tool: `emerald_exchange_get_historical(symbol=..., period="1y")`

### Step 2: feature-engineering
Generate alpha factors with IC/IR scoring.
Tool: `emerald_signals_alpha(ticker=...)`

### Step 3: regime-detection
Classify current market regime (Bull/Bear/Sideways/Crisis).
Tool: `emerald_signals_regime(ticker=...)`

### Step 4: signal-fusion
Bayesian fusion of all signal sources.
Tool: `emerald_signals_fuse(ticker=...)`

### Step 5: kg-persist
Store AlphaFactor and TradingSignal nodes in KG.
Tool: `graph_write(action="add_node", node_type="AlphaFactor", ...)`

## Steps

1. Fetch the universe data with `emerald_exchange_get_historical(symbol=..., period="1y")`. Verify that the response contains rows for every symbol requested.
2. Score alpha factors with `emerald_signals_alpha(ticker=...)`. Verify that each factor carries IC and IR values.
3. Classify the regime with `emerald_signals_regime(ticker=...)`. Verify that the result is one of Bull, Bear, Sideways or Crisis.
4. Fuse the signals with `emerald_signals_fuse(ticker=...)`. Verify that the output has one fused signal per ticker.
5. Persist results with `graph_write(action="add_node", node_type="AlphaFactor", ...)`. Verify that a read-back such as `graph_query` returns the new `AlphaFactor` and `TradingSignal` nodes.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Historical data call returns empty | Wrong symbol or period, or the market-data connector is down | Check the symbol spelling and re-call `emerald_exchange_get_historical` with a shorter `period` such as `3mo`. |
| Fusion has too few inputs | Alpha or regime step failed for the ticker | Re-run steps 2 and 3 for that ticker before calling `emerald_signals_fuse`. |
| `graph_write` is rejected | arbora unreachable or node_type not in the ontology | Confirm the arbora MCP server responds, and use the exact `AlphaFactor` / `TradingSignal` node types. |

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — data-ingest; Step 2 — feature-engineering; Step 3 — regime-detection; Step 4 — signal-fusion; Step 5 — kg-persist

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
