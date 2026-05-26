---
name: github_issue_sdd_planner
description: >-
  Retrieves reported issues for a repository from GitHub, validates their correctness, investigates their root cause, and generates high-fidelity Spec-Driven Development (SDD) specifications and implementation plans within the project's .specify/ workspace directory.
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
tags: ['github', 'sdd', 'planning', 'spec-generator', 'github-agent']
concept: CONCEPT:DEV-001
---

# Github Issue Sdd Planner Workflow

**CONCEPT:DEV-001**

Retrieves reported issues for a repository from GitHub, validates their correctness, investigates their root cause, and generates high-fidelity Spec-Driven Development (SDD) specifications and implementation plans within the project's .specify/ workspace directory.

## Steps

### Step 0: Github Agent
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Retrieve open issues for the target repository using the github_issues tool with target filters. Target/Repo: {{task}}
Expected: `issues, metadata`

### Step 1: Spec Verifier
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Validate and verify if the reported issues are valid. Investigate the root cause of valid issues by reading relevant source files and checking workspace logs.
Expected: `validation_report, root_cause_analysis`

### Step 2: Spec Generator
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Create high-fidelity Spec-Driven Development (SDD) spec.md files for the validated issues under the repository's .specify/ directory using standard spec templates.
Expected: `spec_markdown, specify_sync`

### Step 3: Task Planner
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Generate a comprehensive execution plan and a structured tasks checklist (tasks.md) mapping out dependencies, file changes, and testing tasks to implement the specs.
Expected: `implementation_plan, tasks_md`

### Step 4: KG Persistence [depends_on: task-planner]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Github Issue Sdd Planner results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
