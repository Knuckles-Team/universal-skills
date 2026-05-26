---
name: pr_review_swarm
description: >-
  Parallel execution workflow for pr review swarm using the Unified Parallel Engine
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
tags: [dev-workflows, pr-review-swarm]
concept: CONCEPT:DEV-001
---

# Pr Review Swarm Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for pr review swarm using the Unified Parallel Engine

## Steps

### Step 1: Security
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute security operations for the Pr Review Swarm workflow.
Expected: `security_artifacts`

### Step 2: Performance
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute performance operations for the Pr Review Swarm workflow.
Expected: `performance_artifacts`

### Step 3: Style
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute style operations for the Pr Review Swarm workflow.
Expected: `style_artifacts`

### Step 4: Correctness
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute correctness operations for the Pr Review Swarm workflow.
Expected: `correctness_artifacts`

### Step 5: Test Coverage
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute test coverage operations for the Pr Review Swarm workflow.
Expected: `test_coverage_artifacts`

### Step 6: Merge Decision [depends_on: security, performance, style, correctness, test_coverage]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute merge decision operations for the Pr Review Swarm workflow.
Expected: `merge_decision_artifacts`

### Step 7: KG Persistence [depends_on: merge_decision]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Pr Review Swarm results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
