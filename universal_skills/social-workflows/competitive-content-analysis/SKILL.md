---
name: competitive-content-analysis
skill_type: workflow
description: >-
  Parallel execution workflow for competitive content analysis using the Unified Parallel Engine
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
  tool_assignments:
    content-creator: [graph_query, document_tools]
    media-processor: [graph_analyze]
    publisher-agent: [graph_write]
tags: [social, competitive-content-analysis]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.1.0'
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

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Scrape Content
- **After level 0:** Step 2 — Analyze Frequency Topics
- **After level 1:** Step 3 — Gap Report
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
