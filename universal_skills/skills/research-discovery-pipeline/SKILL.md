---
name: research-discovery-pipeline
skill_type: workflow
description: >-
  Search for papers, explore categories, and download relevant publications for offline analysis.
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
  tool_assignments:
    search-agent: [sx_search, graph_query]
    analyzer-agent: [graph_analyze, sx_storage]
    synthesizer-agent: [graph_analyze, document_tools]
tags: ['arxiv', 'papers', 'discovery', 'summarization']
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.7.0'
---

# Research Discovery Pipeline Workflow

**CONCEPT:RESEARCH-001**

Search for papers, explore categories, and download relevant publications for offline analysis.

## Steps

1. List available research paper sources and categories with `sx_search` and `graph_query`. Verify that the `source` and `categories` outputs are non-empty.
2. Search for recent papers on the requested topic with `graph_analyze` and `sx_storage`. Verify that the returned `paper` list has titles and identifiers.
3. Get details on the most relevant paper with `graph_analyze` and `document_tools`. Verify that `abstract` and `author` are present for the chosen paper.
4. Persist the results as typed nodes and edges with `graph_write`. Verify that a follow-up `graph_query` returns the new nodes linked to existing domain entities.

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

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Search returns no papers | The query is too narrow or the source is down | Broaden the topic keywords and query another source with `sx_search`. |
| Paper details are incomplete | The record lacks an abstract | Select the next most relevant paper from the search results and fetch its details. |
| `graph_write` persistence is rejected | A node has no type or no link target | Re-issue `graph_write` with a typed node and an edge to an entity located first with `graph_query`. |
| `graph_orchestrate` cannot run the DAG | arbora is unreachable | Skip the offload and execute the steps natively in dependency order as described under `## Execution`. |

## Output
- Research Discovery Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Search Papers; Step 1 — Analyze Papers; Step 2 — Synthesize Papers
- **After level 0:** Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
