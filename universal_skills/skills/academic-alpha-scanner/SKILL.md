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
  version: '1.7.0'
  author: Knuckles-Team
---

# Academic Alpha Scanner Workflow

Compose the package-owned ScholarX skill and named universal atomic skills. Keep
research findings and backtest results clearly separate from investment advice or
live-order execution.

## Inputs

Provide the research question, markets, asset universe, date range, source filters,
candidate-selection criteria, data constraints, and backtest assumptions.

## Steps

1. Collect candidate papers by invoking `$scholarx-operations` with the workflow inputs. Verify that `paper_source_packet` is non-empty and lists at least one paper with a source identifier.
2. Audit the evidence by invoking `$citation-auditor` on `paper_source_packet`. Verify that `evidence_audit` has a supported or unsupported verdict for every cited claim.
3. Extract comparable factors by invoking `$factor-hypothesis-extractor` with `paper_source_packet` and `evidence_audit`. Verify that each entry in `candidate_factor_hypotheses` cites a paper from the packet.
4. Obtain market data by invoking `$quant-data-ingest` with `candidate_factor_hypotheses`. Verify that `normalized_market_dataset` covers the requested universe and date range.
5. Backtest the candidates by invoking `$qlib-backtester` with the hypotheses and dataset. Verify that `backtest_report` states its assumptions and limitations, and that no live trade is recommended.


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

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| `paper_source_packet` is empty | Source filters or date range are too narrow for ScholarX | Widen the date range or drop a source filter, then re-invoke `$scholarx-operations` with the revised inputs |
| Hypotheses lack evidence links | `evidence_audit` rejected the cited claims | Drop the unsupported papers from the packet and re-invoke `$factor-hypothesis-extractor` on the audited subset |
| Dataset misses the requested universe | `$quant-data-ingest` could not resolve some instruments | Correct the ticker list or data constraints in the inputs and re-run Step 3 for the missing instruments only |
| Backtest fails to start | `normalized_market_dataset` has gaps or the wrong frequency | Re-ingest with the frequency the factor definition requires, and confirm the report lists the new date coverage |

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

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
