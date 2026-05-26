---
name: competitive_content_analysis
description: >-
  Parallel execution workflow for competitive content analysis using the Unified Parallel Engine
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
  tool_assignments:
    content-creator: [graph_query, document_tools]
    media-processor: [graph_analyze]
    publisher-agent: [graph_write]
tags: [social, competitive-content-analysis]
concept: CONCEPT:SOCIAL-001
---

# Competitive Content Analysis Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for competitive content analysis using the Unified Parallel Engine

## Steps

### Step 1: Scrape Content
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute scrape content operations for the Competitive Content Analysis workflow.
Expected: `scrape_content_artifacts`

### Step 2: Analyze Frequency Topics [depends_on: scrape_content]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute analyze frequency topics operations for the Competitive Content Analysis workflow.
Expected: `analyze_frequency_topics_artifacts`

### Step 3: Gap Report [depends_on: analyze_frequency_topics]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute gap report operations for the Competitive Content Analysis workflow.
Expected: `gap_report_artifacts`

### Step 4: KG Persistence [depends_on: gap_report]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Competitive Content Analysis results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
