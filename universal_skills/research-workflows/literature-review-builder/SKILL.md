---
name: literature-review-builder
skill_type: workflow
description: >-
  Parallel execution workflow for literature review builder using the Unified Parallel Engine
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
tags: [research, literature-review-builder]
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.1.0'
---

# Literature Review Builder Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for literature review builder using the Unified Parallel Engine

## Steps

### Step 1: Define Scope
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute define scope operations for the Literature Review Builder workflow.
Expected: `define_scope_artifacts`

### Step 2: Parallel Search [depends_on: define_scope]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute parallel search operations for the Literature Review Builder workflow.
Expected: `parallel_search_artifacts`

### Step 3: Dedupe [depends_on: parallel_search]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute dedupe operations for the Literature Review Builder workflow.
Expected: `dedupe_artifacts`

### Step 4: Summarize [depends_on: dedupe]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute summarize operations for the Literature Review Builder workflow.
Expected: `summarize_artifacts`

### Step 5: Bibliography [depends_on: summarize]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute bibliography operations for the Literature Review Builder workflow.
Expected: `bibliography_artifacts`

### Step 6: KG Persistence [depends_on: bibliography]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Literature Review Builder results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Define Scope
- **After level 0:** Step 2 — Parallel Search
- **After level 1:** Step 3 — Dedupe
- **After level 2:** Step 4 — Summarize
- **After level 3:** Step 5 — Bibliography
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
