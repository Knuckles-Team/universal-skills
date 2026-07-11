---
name: lead-generation-pipeline
skill_type: workflow
description: >-
  Parallel execution workflow for lead generation pipeline using the Unified Parallel Engine
domain: ops-workflows
agent: operations_coordinator
team_config:
  name: operations_team
  task_pattern: operational process coordination
  execution_mode: sequential
  specialist_ids:
    - intake-agent
    - processor-agent
    - validator-agent
    - report-agent
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
    validator-agent: [graph_query]
    report-agent: [graph_write, document_tools]
tags: [ops, lead-generation-pipeline]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.2.0'
---

# Lead Generation Pipeline Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for lead generation pipeline using the Unified Parallel Engine

## Steps

### Step 1: Identify Icp
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute identify icp operations for the Lead Generation Pipeline workflow.
Expected: `identify_icp_artifacts`

### Step 2: Scrape Prospects [depends_on: identify_icp]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute scrape prospects operations for the Lead Generation Pipeline workflow.
Expected: `scrape_prospects_artifacts`

### Step 3: Score [depends_on: scrape_prospects]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute score operations for the Lead Generation Pipeline workflow.
Expected: `score_artifacts`

### Step 4: Enrich [depends_on: score]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute enrich operations for the Lead Generation Pipeline workflow.
Expected: `enrich_artifacts`

### Step 5: Outreach [depends_on: enrich]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute outreach operations for the Lead Generation Pipeline workflow.
Expected: `outreach_artifacts`

### Step 6: KG Persistence [depends_on: outreach]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Lead Generation Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Identify Icp
- **After level 0:** Step 2 — Scrape Prospects
- **After level 1:** Step 3 — Score
- **After level 2:** Step 4 — Enrich
- **After level 3:** Step 5 — Outreach
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
