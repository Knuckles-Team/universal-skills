---
name: incident_postmortem_pipeline
description: >-
  Parallel execution workflow for incident postmortem pipeline using the Unified Parallel Engine
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
tags: [dev-workflows, incident-postmortem-pipeline]
concept: CONCEPT:DEV-001
---

# Incident Postmortem Pipeline Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for incident postmortem pipeline using the Unified Parallel Engine

## Steps

### Step 1: Gather Logs
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute gather logs operations for the Incident Postmortem Pipeline workflow.
Expected: `gather_logs_artifacts`

### Step 2: Timeline [depends_on: gather_logs]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute timeline operations for the Incident Postmortem Pipeline workflow.
Expected: `timeline_artifacts`

### Step 3: Root Cause [depends_on: timeline]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute root cause operations for the Incident Postmortem Pipeline workflow.
Expected: `root_cause_artifacts`

### Step 4: Action Items [depends_on: root_cause]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute action items operations for the Incident Postmortem Pipeline workflow.
Expected: `action_items_artifacts`

### Step 5: Doc [depends_on: action_items]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute doc operations for the Incident Postmortem Pipeline workflow.
Expected: `doc_artifacts`

### Step 6: Pr [depends_on: doc]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute pr operations for the Incident Postmortem Pipeline workflow.
Expected: `pr_artifacts`

### Step 7: KG Persistence [depends_on: pr]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Incident Postmortem Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
