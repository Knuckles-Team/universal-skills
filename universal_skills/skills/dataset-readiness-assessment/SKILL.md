---
name: dataset-readiness-assessment
domain: data-workflows
skill_type: workflow
description: Profile a dataset, validate it against reviewed quality rules, and produce
  an owner-confirmed data dictionary. Use when a local CSV, TSV, JSON, or JSON Lines
  dataset must be assessed before analysis, ingestion, governance review, or handoff.
agent: workflow-orchestrator
team_config:
  name: dataset_readiness_assessment_team
  task_pattern: Profile a dataset, validate it against reviewed quality rules, and
    produce an owner-confirmed data dictionary. Use when a local CSV, TSV, JSON, or
    JSON Lines dataset must be assessed before analysis, ingestion, governance review,
    or handoff.
  execution_mode: parallel
  specialist_ids:
  - profiling-specialist
  - quality-specialist
  - documentation-specialist
  tool_assignments:
    profiling-specialist:
    - dataset-profiler
    quality-specialist:
    - data-quality-auditor
    documentation-specialist:
    - data-dictionary-builder
license: MIT
tags:
- data
- readiness
- quality
- documentation
requires: []
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---

# Dataset Readiness Assessment Workflow

Profile a dataset, validate it against reviewed quality rules, and produce an owner-confirmed data dictionary. Use when a local CSV, TSV, JSON, or JSON Lines dataset must be assessed before analysis, ingestion, governance review, or handoff.

## Steps

1. Profile the dataset with the `dataset-profiler` skill (Step 1). Verify that the profile reports the row count, column names and inferred types, and that `ls` shows the dataset file exists.
2. Validate the dataset against the reviewed quality rules with the `data-quality-auditor` skill (Step 2). Verify that the audit lists each rule with a pass or fail and the affected columns.
3. Build the owner-confirmed data dictionary with the `data-dictionary-builder` skill (Step 3). Verify that every profiled column has a dictionary entry and an owner confirmation.

### Step 1: dataset-profiler [depends_on: none]
**Agent**: `profiling-specialist`
**Skill**: `dataset-profiler`

### Step 2: data-quality-auditor [depends_on: dataset-profiler]
**Agent**: `quality-specialist`
**Skill**: `data-quality-auditor`

### Step 3: data-dictionary-builder [depends_on: dataset-profiler]
**Agent**: `documentation-specialist`
**Skill**: `data-dictionary-builder`

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Profiler cannot read the file | Unsupported format or wrong delimiter or encoding | Check the file with `file <path>` and `head -n 3 <path>`, convert to UTF-8 CSV or JSON Lines, and profile again |
| Auditor reports no rules evaluated | No reviewed quality rules were supplied for the dataset | Provide the reviewed rule set path to Step 2 and rerun the audit |
| Dictionary has columns without an owner confirmation | The owner has not reviewed the draft entries | Send the draft to the data owner, record their answers, and regenerate the dictionary |


## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — dataset-profiler
- **After level 0:** Step 2 — data-quality-auditor; Step 3 — data-dictionary-builder

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
