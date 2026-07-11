---
name: research-to-implementation
skill_type: workflow
description: >-
  Parallel execution workflow for research to implementation using the Unified Parallel Engine
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
tags: [research, research-to-implementation]
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.2.0'
---

# Research To Implementation Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for research to implementation using the Unified Parallel Engine

## Steps

### Step 1: Find Paper
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute find paper operations for the Research To Implementation workflow.
Expected: `find_paper_artifacts`

### Step 2: Extract Method [depends_on: find_paper]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute extract method operations for the Research To Implementation workflow.
Expected: `extract_method_artifacts`

### Step 3: Implement [depends_on: extract_method]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute implement operations for the Research To Implementation workflow.
Expected: `implement_artifacts`

### Step 4: Benchmark [depends_on: implement]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute benchmark operations for the Research To Implementation workflow.
Expected: `benchmark_artifacts`

### Step 5: Document [depends_on: benchmark]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute document operations for the Research To Implementation workflow.
Expected: `document_artifacts`

### Step 6: KG Persistence [depends_on: document]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Research To Implementation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Find Paper
- **After level 0:** Step 2 — Extract Method
- **After level 1:** Step 3 — Implement
- **After level 2:** Step 4 — Benchmark
- **After level 3:** Step 5 — Document
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
