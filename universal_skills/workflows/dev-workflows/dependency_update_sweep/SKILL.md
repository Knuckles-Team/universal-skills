---
name: dependency_update_sweep
description: >-
  Parallel execution workflow for dependency update sweep using the Unified Parallel Engine
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
tags: [dev-workflows, dependency-update-sweep]
concept: CONCEPT:DEV-001
---

# Dependency Update Sweep Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for dependency update sweep using the Unified Parallel Engine

## Steps

### Step 1: Check Outdated
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute check outdated operations for the Dependency Update Sweep workflow.
Expected: `check_outdated_artifacts`

### Step 2: Update [depends_on: check_outdated]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute update operations for the Dependency Update Sweep workflow.
Expected: `update_artifacts`

### Step 3: Test [depends_on: update]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute test operations for the Dependency Update Sweep workflow.
Expected: `test_artifacts`

### Step 4: Pr [depends_on: test]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute pr operations for the Dependency Update Sweep workflow.
Expected: `pr_artifacts`

### Step 5: KG Persistence [depends_on: pr]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Dependency Update Sweep results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
