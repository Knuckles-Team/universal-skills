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
  version: '1.2.1'
---

# Ai Research Survey Workflow

**CONCEPT:RESEARCH-001**

Comprehensive AI research survey combining paper search with data science capabilities for analysis.

## Steps

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

## Output
- Ai Research Survey results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — ScholarX Agent-Paper Search; Step 1 — Data Science Mcp; Step 2 — ScholarX KG-RAG Paper Search
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
