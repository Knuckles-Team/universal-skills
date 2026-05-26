---
name: conversation_knowledge_extract
description: >-
  Parallel execution workflow for conversation knowledge extract using the Unified Parallel Engine
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
tags: [research, conversation-knowledge-extract]
concept: CONCEPT:RESEARCH-001
---

# Conversation Knowledge Extract Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for conversation knowledge extract using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Conversation Parse Log
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute fan out per conversation parse log operations for the Conversation Knowledge Extract workflow.
Expected: `fan_out_per_conversation_parse_log_artifacts`

### Step 2: Extract Decisions [depends_on: fan_out_per_conversation_parse_log]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute extract decisions operations for the Conversation Knowledge Extract workflow.
Expected: `extract_decisions_artifacts`

### Step 3: Store As Ki [depends_on: extract_decisions]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute store as ki operations for the Conversation Knowledge Extract workflow.
Expected: `store_as_ki_artifacts`

### Step 4: KG Persistence [depends_on: store_as_ki]
**Agent**: `synthesizer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Conversation Knowledge Extract results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
