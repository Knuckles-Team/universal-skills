---
name: github-issue-sdd-planner
skill_type: workflow
description: >-
  Retrieves reported issues for a repository from GitHub, validates their correctness, investigates their root cause, and generates high-fidelity Spec-Driven Development (SDD) specifications and implementation plans within the project's .specify/ workspace directory.
domain: development-workflows
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
tags: ['github', 'sdd', 'planning', 'speckit-specify', 'github-agent']
concept: CONCEPT:DEV-001
metadata:
  version: '1.6.2'
---

# Github Issue Sdd Planner Workflow

**CONCEPT:DEV-001**

Retrieves reported issues for a repository from GitHub, validates their correctness, investigates their root cause, and generates high-fidelity Spec-Driven Development (SDD) specifications and implementation plans within the project's .specify/ workspace directory.

## Steps

1. Retrieve open issues with the `scanner-agent` using `rep_rm_workspace` and `rep_rm_git`. Verify that `issues` lists the repository's open issues.
2. Validate issues with the `builder-agent` using `rep_rm_projects`. Verify that `root_cause_analysis` exists for each valid issue.
3. Generate specs with the `validator-agent`. Verify that `ls .specify/` shows a `spec.md` per validated issue.
4. Create the plan with the `publisher-agent`. Verify that `tasks_md` is present with dependencies and test tasks.
5. Persist to the Knowledge Graph with `graph_write`. Verify that `graph_query` returns the new nodes.

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

### Step 3: Speckit Tasks
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Generate a comprehensive execution plan and a structured tasks checklist (tasks.md) mapping out dependencies, file changes, and testing tasks to implement the specs.
Expected: `implementation_plan, tasks_md`

### Step 4: KG Persistence [depends_on: speckit-tasks]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| No issues returned | Wrong repository or filter | Check the target `{{task}}` value and rerun the retrieval. |
| `.specify/` missing | Repository not initialised | Create the directory with `mkdir -p .specify` and rerun spec generation. |
| Issue judged invalid | Cannot be reproduced | Record the reason and skip spec generation for it. |

## Output
- Github Issue Sdd Planner results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Github Agent; Step 1 — Spec Verifier; Step 2 — Spec Generator; Step 3 — Task Planner
- **After level 0:** Step 4 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
