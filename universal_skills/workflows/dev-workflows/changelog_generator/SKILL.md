---
name: changelog_generator
description: >-
  Parallel execution workflow for changelog generator using the Unified Parallel Engine
domain: dev-workflows
agent: dev_ops_engineer
team_config:
  name: development_operations_team
  task_pattern: development workflow automation
  execution_mode: parallel
  specialist_ids:
    - scanner-agent
    - builder-agent
    - validator-agent
    - publisher-agent
  tool_assignments:
    scanner-agent: [rep_rm_workspace, rep_rm_git]
    builder-agent: [rep_rm_projects]
    validator-agent: [rep_rm_projects, gl_pipelines]
    publisher-agent: [rep_rm_git, gl_merge_requests]
tags: [dev-workflows, changelog-generator]
concept: CONCEPT:DEV-001
---

# Changelog Generator Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for changelog generator using the Unified Parallel Engine

## Steps

### Step 1: Parse Commits
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute parse commits operations for the Changelog Generator workflow.
Expected: `parse_commits_artifacts`

### Step 2: Classify [depends_on: parse_commits]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute classify operations for the Changelog Generator workflow.
Expected: `classify_artifacts`

### Step 3: Generate Notes [depends_on: classify]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute generate notes operations for the Changelog Generator workflow.
Expected: `generate_notes_artifacts`

### Step 4: Publish [depends_on: generate_notes]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute publish operations for the Changelog Generator workflow.
Expected: `publish_artifacts`

### Step 5: KG Persistence [depends_on: publish]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Changelog Generator results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
