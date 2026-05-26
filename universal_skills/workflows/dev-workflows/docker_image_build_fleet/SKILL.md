---
name: docker_image_build_fleet
description: >-
  Parallel execution workflow for docker image build fleet using the Unified Parallel Engine
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
tags: [dev-workflows, docker-image-build-fleet]
concept: CONCEPT:DEV-001
---

# Docker Image Build Fleet Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for docker image build fleet using the Unified Parallel Engine

## Steps

### Step 1: Build
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute build operations for the Docker Image Build Fleet workflow.
Expected: `build_artifacts`

### Step 2: Scan [depends_on: build]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute scan operations for the Docker Image Build Fleet workflow.
Expected: `scan_artifacts`

### Step 3: Push [depends_on: scan]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute push operations for the Docker Image Build Fleet workflow.
Expected: `push_artifacts`

### Step 4: Update Stack [depends_on: push]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute update stack operations for the Docker Image Build Fleet workflow.
Expected: `update_stack_artifacts`

### Step 5: KG Persistence [depends_on: update_stack]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Docker Image Build Fleet results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
