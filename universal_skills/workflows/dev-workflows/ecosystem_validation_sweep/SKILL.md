---
name: ecosystem_validation_sweep
description: >-
  Parallel execution workflow for ecosystem validation sweep using the Unified Parallel Engine
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
tags: [dev-workflows, ecosystem-validation-sweep]
concept: CONCEPT:DEV-001
---

# Ecosystem Validation Sweep Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for ecosystem validation sweep using the Unified Parallel Engine

## Steps

### Step 1: Install
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute install operations for the Ecosystem Validation Sweep workflow.
Expected: `install_artifacts`

### Step 2: Lint [depends_on: install]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute lint operations for the Ecosystem Validation Sweep workflow.
Expected: `lint_artifacts`

### Step 3: Test [depends_on: lint]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute test operations for the Ecosystem Validation Sweep workflow.
Expected: `test_artifacts`

### Step 4: Report [depends_on: test]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute report operations for the Ecosystem Validation Sweep workflow.
Expected: `report_artifacts`

### Step 5: KG Persistence [depends_on: report]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Ecosystem Validation Sweep results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
