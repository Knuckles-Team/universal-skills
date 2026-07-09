---
name: architecture-review-swarm
description: >-
  Parallel execution workflow for architecture review swarm using the Unified Parallel Engine
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
tags: [dev-workflows, architecture-review-swarm]
concept: CONCEPT:DEV-001
---

# Architecture Review Swarm Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for architecture review swarm using the Unified Parallel Engine

## Steps

### Step 1: C4 Diagram
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute c4 diagram operations for the Architecture Review Swarm workflow.
Expected: `c4_diagram_artifacts`

### Step 2: Dependency Graph
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute dependency graph operations for the Architecture Review Swarm workflow.
Expected: `dependency_graph_artifacts`

### Step 3: Coupling Analysis
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute coupling analysis operations for the Architecture Review Swarm workflow.
Expected: `coupling_analysis_artifacts`

### Step 4: Security
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute security operations for the Architecture Review Swarm workflow.
Expected: `security_artifacts`

### Step 5: Report [depends_on: c4_diagram, dependency_graph, coupling_analysis, security]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute report operations for the Architecture Review Swarm workflow.
Expected: `report_artifacts`

### Step 6: KG Persistence [depends_on: report]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Architecture Review Swarm results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — C4 Diagram; Step 2 — Dependency Graph; Step 3 — Coupling Analysis; Step 4 — Security
- **After level 0:** Step 5 — Report
- **After level 1:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
