---
name: migration-guide-generator
description: >-
  Parallel execution workflow for migration guide generator using the Unified Parallel Engine
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
tags: [dev-workflows, migration-guide-generator]
concept: CONCEPT:DEV-001
---

# Migration Guide Generator Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for migration guide generator using the Unified Parallel Engine

## Steps

### Step 1: Diff Versions
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute diff versions operations for the Migration Guide Generator workflow.
Expected: `diff_versions_artifacts`

### Step 2: Identify Breaking Changes [depends_on: diff_versions]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute identify breaking changes operations for the Migration Guide Generator workflow.
Expected: `identify_breaking_changes_artifacts`

### Step 3: Generate Guide [depends_on: identify_breaking_changes]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute generate guide operations for the Migration Guide Generator workflow.
Expected: `generate_guide_artifacts`

### Step 4: Publish [depends_on: generate_guide]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute publish operations for the Migration Guide Generator workflow.
Expected: `publish_artifacts`

### Step 5: KG Persistence [depends_on: publish]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Migration Guide Generator results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Diff Versions
- **After level 0:** Step 2 — Identify Breaking Changes
- **After level 1:** Step 3 — Generate Guide
- **After level 2:** Step 4 — Publish
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
