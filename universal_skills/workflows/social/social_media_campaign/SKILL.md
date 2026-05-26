---
name: social_media_campaign
description: >-
  Parallel execution workflow for social media campaign using the Unified Parallel Engine
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
tags: [social, social-media-campaign]
concept: CONCEPT:SOCIAL-001
---

# Social Media Campaign Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for social media campaign using the Unified Parallel Engine

## Steps

### Step 1: Draft Post
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute draft post operations for the Social Media Campaign workflow.
Expected: `draft_post_artifacts`

### Step 2: Format [depends_on: draft_post]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute format operations for the Social Media Campaign workflow.
Expected: `format_artifacts`

### Step 3: Schedule [depends_on: format]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute schedule operations for the Social Media Campaign workflow.
Expected: `schedule_artifacts`

### Step 4: Monitor Engagement [depends_on: schedule]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute monitor engagement operations for the Social Media Campaign workflow.
Expected: `monitor_engagement_artifacts`

### Step 5: KG Persistence [depends_on: monitor_engagement]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Social Media Campaign results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
