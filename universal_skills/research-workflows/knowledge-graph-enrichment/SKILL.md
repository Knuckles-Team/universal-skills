---
name: knowledge-graph-enrichment
description: >-
  Parallel execution workflow for knowledge graph enrichment using the Unified Parallel Engine
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
tags: [research, knowledge-graph-enrichment]
concept: CONCEPT:RESEARCH-001
---

# Knowledge Graph Enrichment Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for knowledge graph enrichment using the Unified Parallel Engine

## Steps

### Step 1: Papers
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute papers operations for the Knowledge Graph Enrichment workflow.
Expected: `papers_artifacts`

### Step 2: Code
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute code operations for the Knowledge Graph Enrichment workflow.
Expected: `code_artifacts`

### Step 3: Docs
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute docs operations for the Knowledge Graph Enrichment workflow.
Expected: `docs_artifacts`

### Step 4: Extract Entities [depends_on: papers, code, docs]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute extract entities operations for the Knowledge Graph Enrichment workflow.
Expected: `extract_entities_artifacts`

### Step 5: Kg Ingest [depends_on: extract_entities]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute kg ingest operations for the Knowledge Graph Enrichment workflow.
Expected: `kg_ingest_artifacts`

## Output
- Knowledge Graph Enrichment results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Papers; Step 2 — Code; Step 3 — Docs
- **After level 0:** Step 4 — Extract Entities
- **After level 1:** Step 5 — Kg Ingest

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
