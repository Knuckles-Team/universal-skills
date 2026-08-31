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
  version: '1.3.1'
  author: Genius
---

# ESG Screening Pipeline Workflow

Compose the named atomic skills without adding scoring logic here.

## Inputs

Provide the company universe and the ESG disclosure categories of interest.

## Steps

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

## Output

Return `normalized_esg_dataset` and `quality_report`. Does not compute or assert
a proprietary ESG score.

## Execution

- **Run first:** Step 0 — `$web-search`.
- **After level 0:** Step 1 — `$quant-data-ingest`.
- **After level 1:** Step 2 — `$data-quality-auditor`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
