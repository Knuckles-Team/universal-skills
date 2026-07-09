---
name: skill-workflow-builder-workflow
skill_type: workflow
description: >-
  Parallel execution workflow for skill workflow builder using the Unified Parallel Engine
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
tags: [dev-workflows, skill-workflow-builder]
concept: CONCEPT:DEV-001
metadata:
  version: '1.1.0'
---

# Skill Workflow Builder Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for skill workflow builder using the Unified Parallel Engine

## Steps

### Step 1: Brainstorm
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute brainstorm operations for the Skill Workflow Builder workflow.
Expected: `brainstorm_artifacts`

### Step 2: Spec [depends_on: brainstorm]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute spec operations for the Skill Workflow Builder workflow.
Expected: `spec_artifacts`

### Step 3: Skill Md [depends_on: spec]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute skill md operations for the Skill Workflow Builder workflow.
Expected: `skill_md_artifacts`

### Step 4: Team Yaml [depends_on: skill_md]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute team yaml operations for the Skill Workflow Builder workflow.
Expected: `team_yaml_artifacts`

### Step 5: Test [depends_on: team_yaml]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute test operations for the Skill Workflow Builder workflow.
Expected: `test_artifacts`

### Step 6: Register In Kg [depends_on: test]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute register in kg operations for the Skill Workflow Builder workflow.
Expected: `register_in_kg_artifacts`

## Output
- Skill Workflow Builder results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Brainstorm
- **After level 0:** Step 2 — Spec
- **After level 1:** Step 3 — Skill Md
- **After level 2:** Step 4 — Team Yaml
- **After level 3:** Step 5 — Test
- **After level 4:** Step 6 — Register In Kg

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
