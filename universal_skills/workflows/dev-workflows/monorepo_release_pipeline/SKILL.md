---
name: monorepo_release_pipeline
description: >-
  Parallel execution workflow for monorepo release pipeline using the Unified Parallel Engine
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
tags: [dev-workflows, monorepo-release-pipeline]
concept: CONCEPT:DEV-001
---

# Monorepo Release Pipeline Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for monorepo release pipeline using the Unified Parallel Engine

## Steps

### Step 1: Version Bump
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute version bump operations for the Monorepo Release Pipeline workflow.
Expected: `version_bump_artifacts`

### Step 2: Changelog [depends_on: version_bump]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute changelog operations for the Monorepo Release Pipeline workflow.
Expected: `changelog_artifacts`

### Step 3: Parallel Build Per Package [depends_on: changelog]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute parallel build per package operations for the Monorepo Release Pipeline workflow.
Expected: `parallel_build_per_package_artifacts`

### Step 4: Publish [depends_on: parallel_build_per_package]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute publish operations for the Monorepo Release Pipeline workflow.
Expected: `publish_artifacts`

### Step 5: Tag [depends_on: publish]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute tag operations for the Monorepo Release Pipeline workflow.
Expected: `tag_artifacts`

### Step 6: KG Persistence [depends_on: tag]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Monorepo Release Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
