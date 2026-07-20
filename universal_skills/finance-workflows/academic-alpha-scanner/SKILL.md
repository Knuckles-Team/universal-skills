---
name: academic-alpha-scanner
domain: finance-workflows
skill_type: workflow
description: >-
  Discover academic market-factor research, audit its evidence, extract comparable
  hypotheses, obtain the required market data, and backtest the candidates by
  composing package-owned and universal atomic skills. Use when a quantitative
  researcher wants an evidence-linked screening report for candidate alpha factors,
  not live trading or investment advice.
license: MIT
requires:
  - scholarx
  - scholarx-operations
agent: quant-research-orchestrator
team_config:
  name: academic-alpha-scanner-team
  task_pattern: evidence-linked academic alpha screening
  execution_mode: sequential
  specialist_ids:
    - scholarx-operations
    - citation-auditor
    - factor-hypothesis-extractor
    - quant-data-ingest
    - qlib-backtester
tags: [finance, research, alpha, evidence, backtesting]
concept: CONCEPT:EE-011
metadata:
  version: '1.2.1'
  author: Genius
---

# Academic Alpha Scanner Workflow

Compose the package-owned ScholarX skill and named universal atomic skills. Keep
research findings and backtest results clearly separate from investment advice or
live-order execution.

## Inputs

Provide the research question, markets, asset universe, date range, source filters,
candidate-selection criteria, data constraints, and backtest assumptions.

## Steps

### Step 0: scholarx-operations [skill: scholarx-operations]

Invoke `$scholarx-operations` with the workflow inputs.

Expected: `paper_source_packet`

### Step 1: citation-auditor [skill: citation-auditor] [depends_on: Step 0]

Invoke `$citation-auditor` with `paper_source_packet`.

Expected: `evidence_audit`

### Step 2: factor-hypothesis-extractor [skill: factor-hypothesis-extractor] [depends_on: Step 1]

Invoke `$factor-hypothesis-extractor` with `paper_source_packet`, `evidence_audit`,
and the workflow inputs.

Expected: `candidate_factor_hypotheses`

### Step 3: quant-data-ingest [skill: quant-data-ingest] [depends_on: Step 2]

Invoke `$quant-data-ingest` with `candidate_factor_hypotheses` and the workflow
inputs.

Expected: `normalized_market_dataset`

### Step 4: qlib-backtester [skill: qlib-backtester] [depends_on: Step 3]

Invoke `$qlib-backtester` with `candidate_factor_hypotheses`,
`normalized_market_dataset`, and the workflow inputs.

Expected: `backtest_report`

## Output

Return `paper_source_packet`, `evidence_audit`, `candidate_factor_hypotheses`, and
`backtest_report`, including the assumptions and limitations emitted by each skill.
Do not place or recommend live trades.

## Execution

- **Run first:** Step 0 — `$scholarx-operations`.
- **After Step 0:** Step 1 — `$citation-auditor`.
- **After Step 1:** Step 2 — `$factor-hypothesis-extractor`.
- **After Step 2:** Step 3 — `$quant-data-ingest`.
- **After Step 3:** Step 4 — `$qlib-backtester`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
