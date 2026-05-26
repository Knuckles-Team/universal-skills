---
name: blog_post_generator
description: >-
  Parallel execution workflow for blog post generator using the Unified Parallel Engine
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
tags: [social, blog-post-generator]
concept: CONCEPT:SOCIAL-001
---

# Blog Post Generator Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for blog post generator using the Unified Parallel Engine

## Steps

### Step 1: Research Topic
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute research topic operations for the Blog Post Generator workflow.
Expected: `research_topic_artifacts`

### Step 2: Outline [depends_on: research_topic]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute outline operations for the Blog Post Generator workflow.
Expected: `outline_artifacts`

### Step 3: Draft [depends_on: outline]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute draft operations for the Blog Post Generator workflow.
Expected: `draft_artifacts`

### Step 4: Edit [depends_on: draft]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute edit operations for the Blog Post Generator workflow.
Expected: `edit_artifacts`

### Step 5: Seo Optimize [depends_on: edit]
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute seo optimize operations for the Blog Post Generator workflow.
Expected: `seo_optimize_artifacts`

### Step 6: Publish [depends_on: seo_optimize]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute publish operations for the Blog Post Generator workflow.
Expected: `publish_artifacts`

### Step 7: KG Persistence [depends_on: publish]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Blog Post Generator results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
