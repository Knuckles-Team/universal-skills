---
name: skill-graph-rebuild
skill_type: workflow
description: >-
  Parallel execution workflow for skill graph rebuild using the Unified Parallel Engine
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
tags: [dev-workflows, skill-graph-rebuild]
concept: CONCEPT:DEV-001
metadata:
  version: '1.1.0'
---

# Skill Graph Rebuild Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for skill graph rebuild using the Unified Parallel Engine

## Steps

### Step 1: Parse Skill Md
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute parse skill md operations for the Skill Graph Rebuild workflow.
Expected: `parse_skill_md_artifacts`

### Step 2: Extract Deps [depends_on: parse_skill_md]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute extract deps operations for the Skill Graph Rebuild workflow.
Expected: `extract_deps_artifacts`

### Step 3: Build Graph [depends_on: extract_deps]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute build graph operations for the Skill Graph Rebuild workflow.
Expected: `build_graph_artifacts`

### Step 4: Kg Sync [depends_on: build_graph]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute kg sync operations for the Skill Graph Rebuild workflow.
Expected: `kg_sync_artifacts`

## Output
- Skill Graph Rebuild results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Parse Skill Md
- **After level 0:** Step 2 — Extract Deps
- **After level 1:** Step 3 — Build Graph
- **After level 2:** Step 4 — Kg Sync

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
