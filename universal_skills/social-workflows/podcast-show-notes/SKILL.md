---
name: podcast-show-notes
description: >-
  Parallel execution workflow for podcast show notes using the Unified Parallel Engine
domain: social
agent: content_strategist
team_config:
  name: content_creation_team
  task_pattern: content creation and social media management
  execution_mode: sequential
  specialist_ids:
    - content-creator
    - media-processor
    - publisher-agent
    - analytics-agent
  tool_assignments:
    content-creator: [graph_query, document_tools]
    media-processor: [graph_analyze]
    publisher-agent: [graph_write]
    analytics-agent: [graph_query, graph_analyze]
tags: [social, podcast-show-notes]
concept: CONCEPT:SOCIAL-001
---

# Podcast Show Notes Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for podcast show notes using the Unified Parallel Engine

## Steps

### Step 1: Transcribe
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute transcribe operations for the Podcast Show Notes workflow.
Expected: `transcribe_artifacts`

### Step 2: Summarize [depends_on: transcribe]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute summarize operations for the Podcast Show Notes workflow.
Expected: `summarize_artifacts`

### Step 3: Extract Topics [depends_on: summarize]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute extract topics operations for the Podcast Show Notes workflow.
Expected: `extract_topics_artifacts`

### Step 4: Generate Notes [depends_on: extract_topics]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute generate notes operations for the Podcast Show Notes workflow.
Expected: `generate_notes_artifacts`

### Step 5: Publish [depends_on: generate_notes]
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute publish operations for the Podcast Show Notes workflow.
Expected: `publish_artifacts`

### Step 6: KG Persistence [depends_on: publish]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Podcast Show Notes results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Transcribe
- **After level 0:** Step 2 — Summarize
- **After level 1:** Step 3 — Extract Topics
- **After level 2:** Step 4 — Generate Notes
- **After level 3:** Step 5 — Publish
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
