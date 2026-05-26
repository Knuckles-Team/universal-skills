---
name: performance_benchmark_suite
description: >-
  Parallel execution workflow for performance benchmark suite using the Unified Parallel Engine
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
tags: [dev-workflows, performance-benchmark-suite]
concept: CONCEPT:DEV-001
---

# Performance Benchmark Suite Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for performance benchmark suite using the Unified Parallel Engine

## Steps

### Step 1: Profile
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute profile operations for the Performance Benchmark Suite workflow.
Expected: `profile_artifacts`

### Step 2: Identify Bottlenecks [depends_on: profile]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute identify bottlenecks operations for the Performance Benchmark Suite workflow.
Expected: `identify_bottlenecks_artifacts`

### Step 3: Optimize [depends_on: identify_bottlenecks]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute optimize operations for the Performance Benchmark Suite workflow.
Expected: `optimize_artifacts`

### Step 4: Benchmark [depends_on: optimize]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute benchmark operations for the Performance Benchmark Suite workflow.
Expected: `benchmark_artifacts`

### Step 5: KG Persistence [depends_on: benchmark]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Performance Benchmark Suite results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
