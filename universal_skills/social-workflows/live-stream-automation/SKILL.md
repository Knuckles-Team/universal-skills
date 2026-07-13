---
name: live-stream-automation
skill_type: workflow
description: >-
  Parallel execution workflow for live stream automation using the Unified Parallel Engine
domain: social-workflows
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
tags: [social, live-stream-automation]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.2.1'
---

# Live Stream Automation Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for live stream automation using the Unified Parallel Engine

## Steps

### Step 1: Prepare Title
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute prepare title operations for the Live Stream Automation workflow.
Expected: `prepare_title_artifacts`

### Step 2: Configure Obs [depends_on: prepare_title]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute configure obs operations for the Live Stream Automation workflow.
Expected: `configure_obs_artifacts`

### Step 3: Announce [depends_on: configure_obs]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute announce operations for the Live Stream Automation workflow.
Expected: `announce_artifacts`

### Step 4: Engage Chat [depends_on: announce]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute engage chat operations for the Live Stream Automation workflow.
Expected: `engage_chat_artifacts`

### Step 5: Post Stream Summary [depends_on: engage_chat]
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute post stream summary operations for the Live Stream Automation workflow.
Expected: `post_stream_summary_artifacts`

### Step 6: KG Persistence [depends_on: post_stream_summary]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Live Stream Automation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Prepare Title
- **After level 0:** Step 2 — Configure Obs
- **After level 1:** Step 3 — Announce
- **After level 2:** Step 4 — Engage Chat
- **After level 3:** Step 5 — Post Stream Summary
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
