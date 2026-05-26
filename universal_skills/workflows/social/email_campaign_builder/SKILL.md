---
name: email_campaign_builder
description: >-
  Parallel execution workflow for email campaign builder using the Unified Parallel Engine
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
tags: [social, email-campaign-builder]
concept: CONCEPT:SOCIAL-001
---

# Email Campaign Builder Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for email campaign builder using the Unified Parallel Engine

## Steps

### Step 1: Segment Audience
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute segment audience operations for the Email Campaign Builder workflow.
Expected: `segment_audience_artifacts`

### Step 2: Write Variants [depends_on: segment_audience]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute write variants operations for the Email Campaign Builder workflow.
Expected: `write_variants_artifacts`

### Step 3: A B Test [depends_on: write_variants]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute a b test operations for the Email Campaign Builder workflow.
Expected: `a_b_test_artifacts`

### Step 4: Send [depends_on: a_b_test]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute send operations for the Email Campaign Builder workflow.
Expected: `send_artifacts`

### Step 5: Analyze [depends_on: send]
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute analyze operations for the Email Campaign Builder workflow.
Expected: `analyze_artifacts`

### Step 6: KG Persistence [depends_on: analyze]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Email Campaign Builder results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
