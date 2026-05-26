---
name: type_coverage_campaign
description: >-
  Parallel execution workflow for type coverage campaign using the Unified Parallel Engine
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
tags: [dev-workflows, type-coverage-campaign]
concept: CONCEPT:DEV-001
---

# Type Coverage Campaign Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for type coverage campaign using the Unified Parallel Engine

## Steps

### Step 1: Pyright Mypy Analysis
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute pyright mypy analysis operations for the Type Coverage Campaign workflow.
Expected: `pyright_mypy_analysis_artifacts`

### Step 2: Add Types [depends_on: pyright_mypy_analysis]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute add types operations for the Type Coverage Campaign workflow.
Expected: `add_types_artifacts`

### Step 3: Test [depends_on: add_types]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute test operations for the Type Coverage Campaign workflow.
Expected: `test_artifacts`

### Step 4: Pr [depends_on: test]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute pr operations for the Type Coverage Campaign workflow.
Expected: `pr_artifacts`

### Step 5: KG Persistence [depends_on: pr]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Type Coverage Campaign results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
