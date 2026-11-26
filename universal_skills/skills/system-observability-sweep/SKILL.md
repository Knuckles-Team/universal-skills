---
name: system-observability-sweep
skill_type: workflow
description: >-
  Cross-system health and resource check combining system metrics with Langfuse observability status.
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: infrastructure deployment and operations
  execution_mode: parallel
  specialist_ids:
    - discovery-agent
    - deployer-agent
    - verifier-agent
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
    verifier-agent: [pt_docker, cnt_cm_container_operations]
tags: ['monitoring', 'health', 'cross-system', 'observability']
concept: CONCEPT:INFRA-001
metadata:
  version: '1.6.2'
---

# System Observability Sweep Workflow

**CONCEPT:INFRA-001**

Cross-system health and resource check combining system metrics with Langfuse observability status.

## Steps

1. Collect memory, CPU and disk with `tun_tm_system`. Verify that the output contains memory and CPU readings.
2. Check Langfuse health and list datasets using the `langfuse-mcp` tools. Verify that the health endpoint reports OK.
3. List recent traces with the `langfuse-mcp` trace tool. Verify that at least one trace with a status is returned.
4. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

### Step 0: Systems Manager
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Get the system memory usage, CPU stats, and disk utilization
Expected: `memory, cpu`

### Step 1: inspect-langfuse-health [skill: langfuse-mcp]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Check the Langfuse health endpoint and list all current datasets
Expected: `health, dataset`

### Step 2: list-recent-traces [skill: langfuse-mcp]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

List the most recent traces and their status
Expected: `trace`

### Step 3: KG Persistence [depends_on: Step 1, Step 2]
**Agent**: `verifier-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Langfuse health check fails | Wrong host or keys | Fix the Langfuse host and API keys in the agent environment and call the health tool again. |
| Trace list is empty | No recent activity or wrong project | Select the correct project or widen the time range and list traces again. |
| System stats call errors | SSH host unreachable | Check the host with `tun_tm_hosts` and restore connectivity. |

## Output
- System Observability Sweep results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Systems Manager; Step 1 — inspect-langfuse-health; Step 2 — list-recent-traces
- **After level 0:** Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
