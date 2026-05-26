---
name: agent_benchmark_suite
description: >-
  Parallel execution workflow for agent benchmark suite using the Unified Parallel Engine
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
tags: [dev-workflows, agent-benchmark-suite]
concept: CONCEPT:DEV-001
---

# Agent Benchmark Suite Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for agent benchmark suite using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Agent Standardized Task
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute fan out per agent standardized task operations for the Agent Benchmark Suite workflow.
Expected: `fan_out_per_agent_standardized_task_artifacts`

### Step 2: Measure Latency [depends_on: fan_out_per_agent_standardized_task]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute measure latency operations for the Agent Benchmark Suite workflow.
Expected: `measure_latency_artifacts`

### Step 3: Quality [depends_on: fan_out_per_agent_standardized_task]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute quality operations for the Agent Benchmark Suite workflow.
Expected: `quality_artifacts`

### Step 4: Cost [depends_on: fan_out_per_agent_standardized_task]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute cost operations for the Agent Benchmark Suite workflow.
Expected: `cost_artifacts`

### Step 5: Leaderboard [depends_on: measure_latency, quality, cost]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute leaderboard operations for the Agent Benchmark Suite workflow.
Expected: `leaderboard_artifacts`

### Step 6: KG Persistence [depends_on: leaderboard]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Agent Benchmark Suite results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
