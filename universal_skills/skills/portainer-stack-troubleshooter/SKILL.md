---
name: portainer-stack-troubleshooter
skill_type: workflow
description: >-
  Identifies stopped or unhealthy containers inside Portainer stacks, aggregates logs, and creates a step-by-step resolution plan using portainer-agent and tunnel-manager.
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
tags: ['portainer', 'stacks', 'docker', 'troubleshooting', 'portainer-agent', 'tunnel-manager']
concept: CONCEPT:INFRA-001
metadata:
  version: '1.6.2'
---

# Portainer Stack Troubleshooter Workflow

**CONCEPT:INFRA-001**

Identifies stopped or unhealthy containers inside Portainer stacks, aggregates logs, and creates a step-by-step resolution plan using portainer-agent and tunnel-manager.

## Steps

1. Retrieve the stack list and all containers with `portainer_get_stacks` and `portainer_list_containers`. Verify that `containers_status` includes both running and stopped containers.
2. Isolate unhealthy, degraded or stopped containers from `containers_status` and render the triage dashboard. Verify that every failed stack in `portainer_stacks` appears in `stack_triage_dashboard`.
3. Fetch logs for each failed container with `portainer_get_container_logs` and propose stack-level updates or restarts. Verify that `resolution_plan` cites a log line for every failed container.
4. Persist the results as typed nodes and edges with `graph_write`. Verify that a follow-up `graph_query` returns the new nodes linked to existing domain entities.

### Step 0: inspect-portainer-stacks [skill: portainer-agent]
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Retrieve active stacks list using the portainer_get_stacks tool, and retrieve the full list of running and stopped containers using the portainer_list_containers tool.
Expected: `portainer_stacks, containers_status`

### Step 1: User Interaction
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Scan containers_status to isolate unhealthy, degraded, or stopped instances. Construct a visual status dashboard highlighting failed stacks and down services.
Expected: `stack_triage_dashboard`

### Step 2: diagnose-portainer-stack [skill: portainer-agent]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

For the identified failed containers, fetch the diagnostic logs using the portainer_get_container_logs tool. Suggest precise stack-level updates or restart commands.
Expected: `container_diagnostics, resolution_plan`

### Step 3: KG Persistence [depends_on: Step 0, Step 2]
**Agent**: `verifier-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Container list is empty | The Portainer endpoint is wrong or the token expired | Check the endpoint with `portainer_get_stacks` and refresh the Portainer credentials before retrying the listing. |
| Logs are missing for a failed container | The container was already removed or the log driver is not readable | Inspect the container state with `portainer_list_containers` and fall back to the stack events for the diagnosis. |
| `graph_write` persistence is rejected | A node has no type or no link target | Re-issue `graph_write` with a typed node and an edge to an entity located first with `graph_query`. |
| `graph_orchestrate` cannot run the DAG | arbora is unreachable | Skip the offload and execute the steps natively in dependency order as described under `## Execution`. |

## Output
- Portainer Stack Troubleshooter results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — inspect-portainer-stacks; Step 1 — User Interaction; Step 2 — diagnose-portainer-stack
- **After level 0:** Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
