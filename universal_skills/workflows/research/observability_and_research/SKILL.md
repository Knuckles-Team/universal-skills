---
name: observability_and_research
description: >-
  Combined observability check with research discovery. Validates Langfuse is healthy while concurrently searching for papers on agent observability.
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
tags: ['observability', 'research', 'langfuse', 'cross-domain']
concept: CONCEPT:RESEARCH-001
---

# Observability And Research Workflow

**CONCEPT:RESEARCH-001**

Combined observability check with research discovery. Validates Langfuse is healthy while concurrently searching for papers on agent observability.

## Steps

### Step 0: Langfuse Mcp
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Check Langfuse health, list all score configs, and list all datasets
Expected: `health, score, dataset`

### Step 1: Scholarx Mcp
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Search for recent papers on LLM observability and agent tracing
Expected: `paper, observability`

### Step 2: Langfuse Mcp
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

List all current projects in the Langfuse instance
Expected: `project`

### Step 3: KG Persistence [depends_on: langfuse-mcp]
**Agent**: `synthesizer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Observability And Research results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Langfuse Mcp; Step 1 — Scholarx Mcp; Step 2 — Langfuse Mcp
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
