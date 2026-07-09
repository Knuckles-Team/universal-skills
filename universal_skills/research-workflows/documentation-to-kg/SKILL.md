---
name: documentation-to-kg
skill_type: workflow
description: >-
  Parallel execution workflow for documentation to kg using the Unified Parallel Engine
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
tags: [research, documentation-to-kg]
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.0.2'
---

# Documentation To Kg Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for documentation to kg using the Unified Parallel Engine

## Steps

### Step 1: Parse Markdown
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute parse markdown operations for the Documentation To Kg workflow.
Expected: `parse_markdown_artifacts`

### Step 2: Extract Concepts [depends_on: parse_markdown]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute extract concepts operations for the Documentation To Kg workflow.
Expected: `extract_concepts_artifacts`

### Step 3: Entity Resolution [depends_on: extract_concepts]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute entity resolution operations for the Documentation To Kg workflow.
Expected: `entity_resolution_artifacts`

### Step 4: Ingest [depends_on: entity_resolution]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute ingest operations for the Documentation To Kg workflow.
Expected: `ingest_artifacts`

### Step 5: KG Persistence [depends_on: ingest]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Documentation To Kg results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Parse Markdown
- **After level 0:** Step 2 — Extract Concepts
- **After level 1:** Step 3 — Entity Resolution
- **After level 2:** Step 4 — Ingest
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
