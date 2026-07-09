---
name: alternative_data_pipeline
description: >-
  Parallel execution workflow for alternative data pipeline using the Unified Parallel Engine
domain: finance
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
tags: [finance, alternative-data-pipeline]
concept: CONCEPT:EE-011
---

# Alternative Data Pipeline Workflow

**CONCEPT:EE-011**

Parallel execution workflow for alternative data pipeline using the Unified Parallel Engine

## Steps

### Step 1: Satellite
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute satellite operations for the Alternative Data Pipeline workflow.
Expected: `satellite_artifacts`

### Step 2: Social
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute social operations for the Alternative Data Pipeline workflow.
Expected: `social_artifacts`

### Step 3: Web Traffic
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute web traffic operations for the Alternative Data Pipeline workflow.
Expected: `web_traffic_artifacts`

### Step 4: Patent Data
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute patent data operations for the Alternative Data Pipeline workflow.
Expected: `patent_data_artifacts`

### Step 5: Feature Engineer [depends_on: satellite, social, web_traffic, patent_data]
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute feature engineer operations for the Alternative Data Pipeline workflow.
Expected: `feature_engineer_artifacts`

### Step 6: KG Persistence [depends_on: feature_engineer]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Alternative Data Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Satellite; Step 2 — Social; Step 3 — Web Traffic; Step 4 — Patent Data
- **After level 0:** Step 5 — Feature Engineer
- **After level 1:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
