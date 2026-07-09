---
name: x-social-intelligence-pipeline
skill_type: workflow
description: >-
  Parallel execution workflow for x social intelligence pipeline using the Unified Parallel Engine
domain: research-workflows
agent: research_coordinator
team_config:
  name: research_discovery_team
  task_pattern: research discovery and knowledge synthesis
  execution_mode: parallel
  specialist_ids:
    - search-agent
    - analyzer-agent
    - synthesizer-agent
    - ingestor-agent
  tool_assignments:
    search-agent: [sx_search, graph_query]
    analyzer-agent: [graph_analyze, sx_storage]
    synthesizer-agent: [graph_analyze, document_tools]
    ingestor-agent: [graph_write, kg_graph_ingest]
tags: [research, x-social-intelligence-pipeline]
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.0.2'
---

# X Social Intelligence Pipeline Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for x social intelligence pipeline using the Unified Parallel Engine

## Steps

### Step 1: Search X
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute search x operations for the X Social Intelligence Pipeline workflow.
Expected: `search_x_artifacts`

### Step 2: Classify [depends_on: search_x]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute classify operations for the X Social Intelligence Pipeline workflow.
Expected: `classify_artifacts`

### Step 3: Score [depends_on: classify]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute score operations for the X Social Intelligence Pipeline workflow.
Expected: `score_artifacts`

### Step 4: Kg Ingest [depends_on: score]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute kg ingest operations for the X Social Intelligence Pipeline workflow.
Expected: `kg_ingest_artifacts`

### Step 5: Evolution Trigger [depends_on: kg_ingest]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute evolution trigger operations for the X Social Intelligence Pipeline workflow.
Expected: `evolution_trigger_artifacts`

## Output
- X Social Intelligence Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Search X
- **After level 0:** Step 2 — Classify
- **After level 1:** Step 3 — Score
- **After level 2:** Step 4 — Kg Ingest
- **After level 3:** Step 5 — Evolution Trigger

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
