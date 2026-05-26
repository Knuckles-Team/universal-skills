---
name: bug_triage_to_fix
description: >-
  Parallel execution workflow for bug triage to fix using the Unified Parallel Engine
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
tags: [dev-workflows, bug-triage-to-fix]
concept: CONCEPT:DEV-001
---

# Bug Triage To Fix Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for bug triage to fix using the Unified Parallel Engine

## Steps

### Step 1: Triage
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute triage operations for the Bug Triage To Fix workflow.
Expected: `triage_artifacts`

### Step 2: Reproduce [depends_on: triage]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute reproduce operations for the Bug Triage To Fix workflow.
Expected: `reproduce_artifacts`

### Step 3: Diagnose [depends_on: reproduce]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute diagnose operations for the Bug Triage To Fix workflow.
Expected: `diagnose_artifacts`

### Step 4: Fix [depends_on: diagnose]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute fix operations for the Bug Triage To Fix workflow.
Expected: `fix_artifacts`

### Step 5: Test [depends_on: fix]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute test operations for the Bug Triage To Fix workflow.
Expected: `test_artifacts`

### Step 6: Pr [depends_on: test]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute pr operations for the Bug Triage To Fix workflow.
Expected: `pr_artifacts`

### Step 7: KG Persistence [depends_on: pr]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Bug Triage To Fix results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
