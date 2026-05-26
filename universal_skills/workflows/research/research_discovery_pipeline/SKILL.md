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

### Step 0: Scholarx Mcp
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

List available research paper sources and their categories
Expected: `source, categories`

### Step 1: Scholarx Mcp
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Search for recent papers on multi-agent orchestration systems
Expected: `paper, agent`

### Step 2: Scholarx Mcp
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Get details on the most relevant paper from the search results
Expected: `abstract, author`

### Step 3: KG Persistence [depends_on: scholarx-mcp]
**Agent**: `synthesizer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Research Discovery Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
