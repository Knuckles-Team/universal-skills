---
name: langfuse-agent-tracer
skill_type: workflow
description: >-
  Automatically queries Langfuse sessions and traces to isolate agent-utilities execution runs and diagnose spawned agent orchestration errors or performance drops.
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
  tool_assignments:
    scanner-agent: [rep_rm_workspace, rep_rm_git]
    builder-agent: [rep_rm_projects]
    validator-agent: [rep_rm_projects, gl_pipelines]
tags: ['langfuse', 'telemetry', 'tracing', 'monitoring', 'debugging', 'langfuse-mcp']
concept: CONCEPT:DEV-001
metadata:
  version: '1.2.1'
---

# Langfuse Agent Tracer Workflow

**CONCEPT:DEV-001**

Automatically queries Langfuse sessions and traces to isolate agent-utilities execution runs and diagnose spawned agent orchestration errors or performance drops.

## Steps

### Step 0: Langfuse Mcp
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Retrieve lists of traces or recent sessions filtered by tags representing spawned agents or the agent orchestrator using trace_list or sessions_list actions.
Expected: `trace_list_data, active_sessions`

### Step 1: User Interaction
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Present a structured dashboard of agent executions, highlighting traces with warning levels, high latencies, or error logs. Prompt the user to select an execution trace for deep analysis.
Expected: `selected_trace_id, diagnosis_notes`

### Step 2: Langfuse Mcp
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Retrieve complete telemetry span trees, inputs, outputs, and prompt details for the selected execution trace using the trace_get action.
Expected: `trace_span_details`

### Step 3: KG Persistence [depends_on: langfuse-mcp]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Langfuse Agent Tracer results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Langfuse Mcp; Step 1 — User Interaction; Step 2 — Langfuse Mcp
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
