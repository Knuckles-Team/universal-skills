---
name: documentation-site-builder
skill_type: workflow
description: >-
  Parallel execution workflow for documentation site builder using the Unified Parallel Engine
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
tags: [social, documentation-site-builder]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.2.0'
---

# Documentation Site Builder Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for documentation site builder using the Unified Parallel Engine

## Steps

### Step 1: Extract From Code
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute extract from code operations for the Documentation Site Builder workflow.
Expected: `extract_from_code_artifacts`

### Step 2: Write Docs [depends_on: extract_from_code]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute write docs operations for the Documentation Site Builder workflow.
Expected: `write_docs_artifacts`

### Step 3: Generate Api Ref [depends_on: write_docs]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute generate api ref operations for the Documentation Site Builder workflow.
Expected: `generate_api_ref_artifacts`

### Step 4: Deploy [depends_on: generate_api_ref]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute deploy operations for the Documentation Site Builder workflow.
Expected: `deploy_artifacts`

### Step 5: KG Persistence [depends_on: deploy]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Documentation Site Builder results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Extract From Code
- **After level 0:** Step 2 — Write Docs
- **After level 1:** Step 3 — Generate Api Ref
- **After level 2:** Step 4 — Deploy
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
