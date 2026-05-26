---
name: multi_repo_refactor
description: >-
  Parallel execution workflow for multi repo refactor using the Unified Parallel Engine
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
tags: [dev-workflows, multi-repo-refactor]
concept: CONCEPT:DEV-001
---

# Multi Repo Refactor Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for multi repo refactor using the Unified Parallel Engine

## Steps

### Step 1: Analyze
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute analyze operations for the Multi Repo Refactor workflow.
Expected: `analyze_artifacts`

### Step 2: Refactor [depends_on: analyze]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute refactor operations for the Multi Repo Refactor workflow.
Expected: `refactor_artifacts`

### Step 3: Test [depends_on: refactor]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute test operations for the Multi Repo Refactor workflow.
Expected: `test_artifacts`

### Step 4: Pr [depends_on: test]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute pr operations for the Multi Repo Refactor workflow.
Expected: `pr_artifacts`

### Step 5: KG Persistence [depends_on: pr]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Multi Repo Refactor results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
