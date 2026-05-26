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
