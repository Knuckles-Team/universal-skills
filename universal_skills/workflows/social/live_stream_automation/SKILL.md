---
name: live_stream_automation
description: >-
  Parallel execution workflow for live stream automation using the Unified Parallel Engine
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
tags: [social, live-stream-automation]
concept: CONCEPT:SOCIAL-001
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
