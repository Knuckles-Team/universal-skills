---
name: paper_replication_pipeline
description: >-
  Parallel execution workflow for paper replication pipeline using the Unified Parallel Engine
domain: research
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
tags: [research, paper-replication-pipeline]
concept: CONCEPT:RESEARCH-001
---

# Paper Replication Pipeline Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for paper replication pipeline using the Unified Parallel Engine

## Steps

### Step 1: Parse Methodology
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute parse methodology operations for the Paper Replication Pipeline workflow.
Expected: `parse_methodology_artifacts`

### Step 2: Extract Code Data [depends_on: parse_methodology]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute extract code data operations for the Paper Replication Pipeline workflow.
Expected: `extract_code_data_artifacts`

### Step 3: Replicate [depends_on: extract_code_data]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute replicate operations for the Paper Replication Pipeline workflow.
Expected: `replicate_artifacts`

### Step 4: Compare Results [depends_on: replicate]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute compare results operations for the Paper Replication Pipeline workflow.
Expected: `compare_results_artifacts`

### Step 5: KG Persistence [depends_on: compare_results]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Paper Replication Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Parse Methodology
- **After level 0:** Step 2 — Extract Code Data
- **After level 1:** Step 3 — Replicate
- **After level 2:** Step 4 — Compare Results
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
