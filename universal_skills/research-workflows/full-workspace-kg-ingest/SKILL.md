---
name: full-workspace-kg-ingest
description: >-
  Parallel execution workflow for full workspace kg ingest using the Unified Parallel Engine
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
tags: [research, full-workspace-kg-ingest]
concept: CONCEPT:RESEARCH-001
---

# Full Workspace Kg Ingest Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for full workspace kg ingest using the Unified Parallel Engine

## Steps

### Step 1: Parse
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute parse operations for the Full Workspace Kg Ingest workflow.
Expected: `parse_artifacts`

### Step 2: Extract Concepts [depends_on: parse]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute extract concepts operations for the Full Workspace Kg Ingest workflow.
Expected: `extract_concepts_artifacts`

### Step 3: Ingest [depends_on: extract_concepts]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute ingest operations for the Full Workspace Kg Ingest workflow.
Expected: `ingest_artifacts`

### Step 4: Build Edges [depends_on: ingest]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute build edges operations for the Full Workspace Kg Ingest workflow.
Expected: `build_edges_artifacts`

### Step 5: KG Persistence [depends_on: build_edges]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Full Workspace Kg Ingest results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Parse
- **After level 0:** Step 2 — Extract Concepts
- **After level 1:** Step 3 — Ingest
- **After level 2:** Step 4 — Build Edges
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
