---
name: strategy-export
skill_type: workflow
description: >-
  Parallel execution workflow for strategy export using the Unified Parallel Engine
domain: finance-workflows
agent: quant_analyst
team_config:
  name: quantitative_trading_team
  task_pattern: quantitative analysis and financial computation
  execution_mode: parallel
  specialist_ids:
    - data-fetcher
    - compute-engine
    - risk-assessor
    - report-generator
  tool_assignments:
    data-fetcher: [graph_query, sx_search]
    compute-engine: [graph_analyze]
    risk-assessor: [graph_query, graph_analyze]
    report-generator: [graph_write, document_tools]
tags: [finance, strategy, export, deployment]
concept: CONCEPT:EE-011
metadata:
  version: '1.6.2'
---

# Strategy Export Workflow

**CONCEPT:EE-011**

>-

## Steps

1. Select a validated strategy with `emerald_strategy_list()`. Verify that the chosen strategy id appears in the returned list.
2. Export it with `emerald_strategy_export(strategy_id=..., format="pinescript")`. Verify that the call returns non-empty source in the target format.
3. Deploy to freqtrade in dry-run mode via the freqtrade backend with `dry_run` enabled. Verify that the freqtrade logs show dry-run and no live orders.
4. Publish to the community registry via meristem `strategy_sharing.py`. Verify that the registry returns a published entry for the strategy id.
5. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

### Step 1: Select Strategy
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Pick a validated strategy from the Knowledge Graph.
Tool: `emerald_strategy_list()`

### Step 2: Export
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Convert to target format (PineScript/MQL5/TDX).
Tool: `emerald_strategy_export(strategy_id=..., format="pinescript")`

### Step 3: Deploy Freqtrade
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Deploy to freqtrade in paper mode for validation.
Tool: Route to freqtrade backend for dry-run.

### Step 4: Share
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Publish to community strategy registry.
Tool: Route to meristem `strategy_sharing.py`.

### Step 5: KG Persistence [depends_on: share]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `emerald_strategy_list` is empty | No validated strategies exist | Run `strategy-tournament` or `walk-forward-validation` first to validate one. |
| Export returns an error for the format | Unsupported format value | Use one of PineScript, MQL5 or TDX as the `format` argument and call `emerald_strategy_export` again. |
| Freqtrade deployment starts live | Config is not in dry-run | Stop it and set `dry_run` to true in the freqtrade config before redeploying. |

## Output
- Strategy Export results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Select Strategy; Step 2 — Export; Step 3 — Deploy Freqtrade; Step 4 — Share
- **After level 0:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
