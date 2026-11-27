---
name: observability-and-research
skill_type: workflow
description: >-
  Combined observability check with research discovery. Validates Langfuse is healthy while concurrently searching for papers on agent observability.
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
tags: ['observability', 'research', 'langfuse', 'cross-domain']
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.7.0'
---

# Observability And Research Workflow

**CONCEPT:RESEARCH-001**

Combined observability check with research discovery. Validates Langfuse is healthy while concurrently searching for papers on agent observability.

## Steps

1. Inventory Langfuse with the `langfuse-mcp` tools for health, score configs and datasets. Verify that `health`, `score` and `dataset` are returned.
2. Search for papers with `sx_search` and the scholarx MCP on LLM observability. Verify that `paper` entries are returned.
3. List Langfuse projects with the `langfuse-mcp` tools. Verify that `project` is non-empty.
4. Persist results with `graph_write`. Verify that a `graph_query` returns the new nodes.

### Step 0: Langfuse Configuration Inventory [skill: langfuse-mcp]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Check Langfuse health, list all score configs, and list all datasets
Expected: `health, score, dataset`

### Step 1: Scholarx Mcp
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Search for recent papers on LLM observability and agent tracing
Expected: `paper, observability`

### Step 2: Langfuse Project Inventory [skill: langfuse-mcp]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

List all current projects in the Langfuse instance
Expected: `project`

### Step 3: KG Persistence [depends_on: Step 2]
**Agent**: `synthesizer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Langfuse health fails | Wrong host or key | Check the Langfuse endpoint and keys, then call the health tool again |
| No papers | Query too narrow | Broaden the `sx_search` query |
| Empty project list | Key lacks scope | Replace the Langfuse key with an organization-level key and list projects again |

## Output
- Observability And Research results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Langfuse Configuration Inventory; Step 1 — Scholarx Mcp; Step 2 — Langfuse Project Inventory
- **After level 0:** Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
