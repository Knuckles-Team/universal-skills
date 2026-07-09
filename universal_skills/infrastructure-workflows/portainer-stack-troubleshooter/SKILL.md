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
  version: '1.2.0'
---

# Portainer Stack Troubleshooter Workflow

**CONCEPT:INFRA-001**

Identifies stopped or unhealthy containers inside Portainer stacks, aggregates logs, and creates a step-by-step resolution plan using portainer-agent and tunnel-manager.

## Steps

### Step 0: Portainer Agent
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Retrieve active stacks list using portainer_stack get_stacks tool, and retrieve the full list of running and stopped containers using portainer_docker docker_list_containers tool.
Expected: `portainer_stacks, containers_status`

### Step 1: User Interaction
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Scan containers_status to isolate unhealthy, degraded, or stopped instances. Construct a visual status dashboard highlighting failed stacks and down services.
Expected: `stack_triage_dashboard`

### Step 2: Portainer Agent
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

For the identified failed containers, fetch the diagnostic logs using portainer_docker docker_get_container_logs tool. Suggest precise stack-level updates or restart commands.
Expected: `container_diagnostics, resolution_plan`

### Step 3: KG Persistence [depends_on: portainer-agent]
**Agent**: `verifier-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Portainer Stack Troubleshooter results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Portainer Agent; Step 1 — User Interaction; Step 2 — Portainer Agent
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
