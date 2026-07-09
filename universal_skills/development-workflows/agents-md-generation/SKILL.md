---
name: agents-md-generation
description: >-
  Parallel execution workflow for agents md generation using the Unified Parallel Engine
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
tags: [dev-workflows, agents-md-generation]
concept: CONCEPT:DEV-001
---

# Agents Md Generation Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for agents md generation using the Unified Parallel Engine

## Steps

### Step 1: Analyze
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute analyze operations for the Agents Md Generation workflow.
Expected: `analyze_artifacts`

### Step 2: Generate Agents Md [depends_on: analyze]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute generate agents md operations for the Agents Md Generation workflow.
Expected: `generate_agents_md_artifacts`

### Step 3: Pr [depends_on: generate_agents_md]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute pr operations for the Agents Md Generation workflow.
Expected: `pr_artifacts`

### Step 4: KG Persistence [depends_on: pr]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Agents Md Generation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Analyze
- **After level 0:** Step 2 — Generate Agents Md
- **After level 1:** Step 3 — Pr
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
