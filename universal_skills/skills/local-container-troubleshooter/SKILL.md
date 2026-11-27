---
name: local-container-troubleshooter
skill_type: workflow
description: >-
  Automatically scans local containers, pulls crash logs, and designs remediation steps to resolve failures using container-manager-mcp.
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
    - dns-configurator
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
    verifier-agent: [pt_docker, cnt_cm_container_operations]
    dns-configurator: [adg_rewrites, td_zones]
tags: ['docker', 'podman', 'local-deploy', 'troubleshooting', 'container-manager-mcp']
concept: CONCEPT:INFRA-001
metadata:
  version: '1.7.0'
---

# Local Container Troubleshooter Workflow

**CONCEPT:INFRA-001**

Automatically scans local containers, pulls crash logs, and designs remediation steps to resolve failures using container-manager-mcp.

## Steps

1. Scan containers with `cm_container_operations` `list_containers` using `all_containers`. Verify that `local_containers_list` includes stopped containers.
2. Filter stopped or unhealthy containers and ask the user to confirm. Verify that `selected_containers` is recorded.
3. Fetch logs with `cm_container_operations` `get_container_logs` using `tail`. Verify that `container_logs` is non-empty for each selected container.
4. Check compose state with `cm_compose_operations` `ps`. Verify that `compose_states` lists each stack.
5. Fuse logs and states into a remediation plan. Verify that `remediation_plan` names a root cause per failed container.
6. Persist with `graph_write`. Verify that `graph_query` returns the new nodes.

### Step 0: scan-local-containers [skill: container-manager-mcp]
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Scan all local container instances (running and stopped) using cm_container_operations list_containers tool with all_containers parameter.
Expected: `local_containers_list`

### Step 1: select-failed-containers [skill: user-interaction]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Filter and present any stopped or unhealthy containers from local_containers_list. Ask the user for confirmation to inspect crash logs.
Expected: `selected_containers`

### Step 2: fetch-failure-logs [skill: container-manager-mcp]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Retrieve log outputs for selected failed containers using cm_container_operations get_container_logs tool with tail parameter.
Expected: `container_logs`

### Step 3: inspect-compose-state [skill: container-manager-mcp]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Check local compose environments using cm_compose_operations ps tool.
Expected: `compose_states`

### Step 4: present-remediation-plan [skill: user-interaction]
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Fuse container logs and compose states to diagnose root failures and formulate automated remediation steps.
Expected: `remediation_plan`

### Step 5: KG Persistence [depends_on: Step 1, Step 4]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| No failed containers | All healthy | Report no action needed and stop. |
| Logs empty | `tail` too small or the container never started | Increase `tail` and inspect `docker inspect` for the exit code. |
| Compose `ps` shows nothing | No compose project in this context | Check the project directory and context and rerun. |

## Output
- Local Container Troubleshooter results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — scan-local-containers; Step 1 — select-failed-containers; Step 2 — fetch-failure-logs; Step 3 — inspect-compose-state; Step 4 — present-remediation-plan
- **After level 0:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
