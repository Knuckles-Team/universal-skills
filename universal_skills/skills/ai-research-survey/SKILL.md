---
name: ai-research-survey
skill_type: workflow
description: >-
  Comprehensive AI research survey combining paper search with data science capabilities for analysis.
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
tags: ['ai', 'survey', 'papers', 'data-science']
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.6.2'
---

# Ai Research Survey Workflow

**CONCEPT:RESEARCH-001**

Comprehensive AI research survey combining paper search with data science capabilities for analysis.

## Steps

1. Search recent agent papers by invoking `$scholarx-mcp` with the `sx_search` tool for large language model agents published in 2025-2026. Verify that the result lists papers with titles and years.
2. Profile a sample dataset by calling the `describe_dataset` tool on the iris dataset. Verify that the output reports the dataset's features and row count.
3. Search knowledge-graph reasoning papers by invoking `$scholarx-mcp` with `sx_search` for retrieval augmented generation. Verify that the result contains papers distinct from Step 0.
4. Persist the results with `graph_write` as typed nodes linked to existing entities. Verify that a `graph_query` for the new nodes returns them with their metadata.


### Step 0: ScholarX Agent-Paper Search [skill: scholarx-mcp]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Search for recent papers on large language model agents published in 2025-2026
Expected: `paper, language, model`

### Step 1: Data Science Mcp
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Describe the iris dataset using the describe_dataset tool to verify data science capabilities
Expected: `dataset, feature`

### Step 2: ScholarX KG-RAG Paper Search [skill: scholarx-mcp]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Search for papers on knowledge graph reasoning and retrieval augmented generation
Expected: `knowledge, graph`

### Step 3: KG Persistence [depends_on: Step 2]
**Agent**: `synthesizer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| `sx_search` returns no papers | Query too specific or ScholarX server unreachable | Broaden the query terms and confirm the `scholarx-mcp` server responds before re-searching |
| `describe_dataset` errors | Data science MCP server is not registered | Check that the data science MCP server is listed in the active MCP configuration and restart it |
| `graph_write` rejects the nodes | Node types or required metadata are missing | Add the typed labels and metadata fields named in the Step 3 text and write again |
| Parallel steps return partial results | One search step timed out | Re-run only the failed step with a shorter query and merge its output into the report |

## Output
- Ai Research Survey results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — ScholarX Agent-Paper Search; Step 1 — Data Science Mcp; Step 2 — ScholarX KG-RAG Paper Search
- **After level 0:** Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
