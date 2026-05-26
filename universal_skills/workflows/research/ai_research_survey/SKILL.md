---
name: ai_research_survey
description: >-
  Comprehensive AI research survey combining paper search with data science capabilities for analysis.
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
tags: ['ai', 'survey', 'papers', 'data-science']
concept: CONCEPT:RESEARCH-001
---

# Ai Research Survey Workflow

**CONCEPT:RESEARCH-001**

Comprehensive AI research survey combining paper search with data science capabilities for analysis.

## Steps

### Step 0: Scholarx Mcp
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Search for recent papers on large language model agents published in 2025-2026
Expected: `paper, language, model`

### Step 1: Data Science Mcp
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Describe the iris dataset using the describe_dataset tool to verify data science capabilities
Expected: `dataset, feature`

### Step 2: Scholarx Mcp
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Search for papers on knowledge graph reasoning and retrieval augmented generation
Expected: `knowledge, graph`

### Step 3: KG Persistence [depends_on: scholarx-mcp]
**Agent**: `synthesizer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Ai Research Survey results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
