---
name: social_media_influencer
description: >-
  Prepares a live stream broadcast title, updates style details, announces the live stream, and engages the audience using owncast-agent tools.
domain: social
agent: content_strategist
team_config:
  name: content_creation_team
  task_pattern: content creation and social media management
  execution_mode: sequential
  specialist_ids:
    - content-creator
    - media-processor
  tool_assignments:
    content-creator: [graph_query, document_tools]
    media-processor: [graph_analyze]
tags: ['social', 'streaming', 'broadcast', 'owncast-agent']
concept: CONCEPT:SOCIAL-001
---

# Social Media Influencer Workflow

**CONCEPT:SOCIAL-001**

Prepares a live stream broadcast title, updates style details, announces the live stream, and engages the audience using owncast-agent tools.

## Steps

### Step 0: Social Media Influencer
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Update the live stream broadcast title, welcome message text, and style customization details using the owncast_objects and owncast_internal tools.
Expected: `stream_status, metadata`

### Step 1: Owncast Agent
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Announce stream live status to connected social networks. Trigger an initial welcome notification message in the live stream chat using owncast_external and owncast_chat tools.
Expected: `system_chat_post, notification`

### Step 2: KG Persistence [depends_on: owncast-agent]
**Agent**: `media-processor`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Social Media Influencer results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
