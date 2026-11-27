---
name: alpha-factor-mining
skill_type: workflow
description: >-
  Compute momentum, fundamental quality, and news sentiment factor signals in parallel to generate a fused target portfolio.
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
tags: [quant, alpha, momentum, sentiment, fundamental, optimization]
concept: CONCEPT:EE-011
metadata:
  version: '1.7.0'
---

# Alpha Factor Mining Workflow

**CONCEPT:EE-011**

Compute momentum, fundamental quality, and news sentiment factor signals in parallel to generate a fused target portfolio.

## Steps

1. Compute technical factors by running Step 1 with `graph_query` and `sx_search` on the tick logs. Verify that `technical-factors` contains momentum, RSI and mean-reversion columns with no empty series.
2. Compute fundamental factors by running Step 2 with `graph_analyze` on filing data. Verify that `fundamental-factors` includes PE, debt-to-equity and gross margin for each instrument.
3. Compute sentiment factors by running Step 3 with `graph_query` and `graph_analyze` on news and transcripts. Verify that `sentiment-factors` has a score per instrument and date.
4. Fuse the three factor sets by running Step 4 with `graph_write` and `document_tools`. Verify that `optimized-portfolio-weights` sum to the target exposure and that the correlation test removed collinear factors.
5. Persist the outputs by running Step 5 with `graph_write`. Verify that a `graph_query` for the new nodes returns the optimized portfolio.


### Step 1: Technical Alpha
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Compute rolling standard momentum, RSI, mean-reversion metrics, and volume-weighted indicators from high-frequency market tick logs.
Expected: `technical-factors`

### Step 2: Fundamental Alpha [depends_on: none]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Extract historical and recent financial filing data, calculating PE, debt-to-equity ratios, and gross margin momentum.
Expected: `fundamental-factors`

### Step 3: Sentiment Alpha [depends_on: none]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Perform natural language sentiment extraction from recent financial news stories, earnings call transcripts, and social media feeds.
Expected: `sentiment-factors`

### Step 4: Factor Fusion [depends_on: technical-alpha, fundamental-alpha, sentiment-alpha]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Synthesize the technical, fundamental, and sentiment signals, perform correlation testing to remove multi-collinearity, and run a risk-budgeted mean-variance optimization.
Expected: `optimized-portfolio-weights`

### Step 5: KG Persistence [depends_on: Factor Fusion]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| A factor series is empty | Tick logs or filings missing for the universe | Narrow the universe to instruments with data and re-run that factor's step |
| Fusion fails on collinearity | Two factors are near-duplicates | Drop the weaker factor from the fusion inputs and re-run Step 4 |
| Optimizer returns infeasible weights | Risk budget is too tight | Relax the risk budget constraint in the Step 4 inputs and re-solve |
| KG write rejected | Required typed node metadata missing | Add the missing fields named in the Step 5 text and call `graph_write` again |

## Output
- Alpha Factor Mining results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Technical Alpha; Step 2 — Fundamental Alpha; Step 3 — Sentiment Alpha
- **After level 0:** Step 4 — Factor Fusion
- **After level 1:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
