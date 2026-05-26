---
name: code_walkthrough_library
description: >-
  Parallel execution workflow for code walkthrough library using the Unified Parallel Engine
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
  tool_assignments:
    scanner-agent: [rep_rm_workspace, rep_rm_git]
    builder-agent: [rep_rm_projects]
    validator-agent: [rep_rm_projects, gl_pipelines]
tags: [dev-workflows, code-walkthrough-library]
concept: CONCEPT:DEV-001
---

# Code Walkthrough Library Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for code walkthrough library using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Feature Analyze
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute fan out per feature analyze operations for the Code Walkthrough Library workflow.
Expected: `fan_out_per_feature_analyze_artifacts`

### Step 2: Interactive Explain [depends_on: fan_out_per_feature_analyze]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute interactive explain operations for the Code Walkthrough Library workflow.
Expected: `interactive_explain_artifacts`

### Step 3: Publish [depends_on: interactive_explain]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute publish operations for the Code Walkthrough Library workflow.
Expected: `publish_artifacts`

### Step 4: KG Persistence [depends_on: publish]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Code Walkthrough Library results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
