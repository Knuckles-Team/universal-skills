---
name: esg-screening-pipeline
skill_type: workflow
description: >-
  Gather publicly disclosed ESG (environmental, social, governance) signals for a
  supplied company universe and structure them into a normalized, validated
  dataset. Use when a researcher needs raw ESG disclosure data assembled for
  downstream screening; this workflow does not compute a proprietary ESG score
  or rating.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: esg-screening-pipeline-team
  task_pattern: public ESG disclosure gathering and validated normalization
  execution_mode: sequential
  specialist_ids:
    - web-search
    - quant-data-ingest
    - data-quality-auditor
tags: [finance, esg, screening, ingestion]
concept: CONCEPT:EE-011
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# ESG Screening Pipeline Workflow

Compose the named atomic skills without adding scoring logic here.

## Inputs

Provide the company universe and the ESG disclosure categories of interest.

## Steps

1. Locate ESG disclosures by invoking `$web-search` with the company universe and categories. Verify that `esg_source_packet` has a source link for each company covered.
2. Normalize the data by invoking `$quant-data-ingest` with `esg_source_packet`. Verify that `normalized_esg_dataset` is stored in Timeseries Memory.
3. Audit quality by invoking `$data-quality-auditor` with `normalized_esg_dataset` and the rule set. Verify that `quality_report` lists pass or fail for each rule.

### Step 0: web-search [skill: web-search]

Invoke `$web-search` with the workflow inputs to locate publicly
disclosed ESG reports and filings for the universe.

Expected: `esg_source_packet`

### Step 1: quant-data-ingest [skill: quant-data-ingest] [depends_on: Step 0]

Invoke `$quant-data-ingest` with `esg_source_packet` to normalize the
disclosed data into the Timeseries Memory backend.

Expected: `normalized_esg_dataset`

### Step 2: data-quality-auditor [skill: data-quality-auditor] [depends_on: Step 1]

Invoke `$data-quality-auditor` with `normalized_esg_dataset` and the
declared rule set.

Expected: `quality_report`

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| A company has no disclosure | No public ESG report exists | Record the gap in `quality_report` and do not infer values. |
| `quality_report` shows many rule failures | Source packets used mismatched units or formats | Fix the normalization in `$quant-data-ingest` and rerun the audit. |
| Request to compute an ESG score | Out of scope | Decline, since the workflow outputs only the dataset and report. |

## Output

Return `normalized_esg_dataset` and `quality_report`. Does not compute or assert
a proprietary ESG score.

## Execution

- **Run first:** Step 0 — `$web-search`.
- **After level 0:** Step 1 — `$quant-data-ingest`.
- **After level 1:** Step 2 — `$data-quality-auditor`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
