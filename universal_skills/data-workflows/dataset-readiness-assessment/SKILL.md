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
  version: '1.2.1'
  author: Genius
---

# Dataset Readiness Assessment Workflow

Profile a dataset, validate it against reviewed quality rules, and produce an owner-confirmed data dictionary. Use when a local CSV, TSV, JSON, or JSON Lines dataset must be assessed before analysis, ingestion, governance review, or handoff.

## Steps

### Step 1: dataset-profiler [depends_on: none]
**Agent**: `profiling-specialist`
**Skill**: `dataset-profiler`

### Step 2: data-quality-auditor [depends_on: dataset-profiler]
**Agent**: `quality-specialist`
**Skill**: `data-quality-auditor`

### Step 3: data-dictionary-builder [depends_on: dataset-profiler]
**Agent**: `documentation-specialist`
**Skill**: `data-dictionary-builder`

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — dataset-profiler
- **After level 0:** Step 2 — data-quality-auditor; Step 3 — data-dictionary-builder

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
