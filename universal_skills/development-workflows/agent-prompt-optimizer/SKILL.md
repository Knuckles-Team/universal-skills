---
name: agent-prompt-optimizer
skill_type: workflow
description: >-
  Parallel execution workflow for agent prompt optimizer using the Unified Parallel Engine
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
tags: [dev-workflows, agent-prompt-optimizer]
concept: CONCEPT:DEV-001
metadata:
  version: '1.0.2'
---

# Agent Prompt Optimizer Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for agent prompt optimizer using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Prompt Benchmark
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute fan out per prompt benchmark operations for the Agent Prompt Optimizer workflow.
Expected: `fan_out_per_prompt_benchmark_artifacts`

### Step 2: Variant Generation [depends_on: fan_out_per_prompt_benchmark]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute variant generation operations for the Agent Prompt Optimizer workflow.
Expected: `variant_generation_artifacts`

### Step 3: A B Eval [depends_on: variant_generation]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute a b eval operations for the Agent Prompt Optimizer workflow.
Expected: `a_b_eval_artifacts`

### Step 4: Select Best [depends_on: a_b_eval]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute select best operations for the Agent Prompt Optimizer workflow.
Expected: `select_best_artifacts`

### Step 5: KG Persistence [depends_on: select_best]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Agent Prompt Optimizer results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Prompt Benchmark
- **After level 0:** Step 2 — Variant Generation
- **After level 1:** Step 3 — A B Eval
- **After level 2:** Step 4 — Select Best
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
