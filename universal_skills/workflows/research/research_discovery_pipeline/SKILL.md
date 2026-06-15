---
name: research_discovery_pipeline
description: >-
  Search for papers, explore categories, and download relevant publications for offline analysis.
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
  tool_assignments:
    search-agent: [sx_search, graph_query]
    analyzer-agent: [graph_analyze, sx_storage]
    synthesizer-agent: [graph_analyze, document_tools]
tags: ['arxiv', 'papers', 'discovery', 'summarization']
concept: CONCEPT:RESEARCH-001
---

# Research Discovery Pipeline Workflow

**CONCEPT:RESEARCH-001**

Search for papers, explore categories, and download relevant publications for offline analysis.

## Steps

### Step 0: Search Papers
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

List available research paper sources and their categories
Expected: `source, categories`

### Step 1: Analyze Papers
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Search for recent papers on multi-agent orchestration systems
Expected: `paper, agent`

### Step 2: Synthesize Papers
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Get details on the most relevant paper from the search results
Expected: `abstract, author`

### Step 3: KG Persistence [depends_on: synthesize_papers]
**Agent**: `synthesizer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Research Discovery Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Search Papers; Step 1 — Analyze Papers; Step 2 — Synthesize Papers
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
