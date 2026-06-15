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

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Conversation Parse Log
- **After level 0:** Step 2 — Extract Decisions
- **After level 1:** Step 3 — Store As Ki
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
