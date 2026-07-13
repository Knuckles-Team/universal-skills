---
name: deploy-platform-stack
skill_type: workflow
description: >-
  End-to-end deployment of an infrastructure platform using docker-compose files and Portainer MCP.
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: infrastructure deployment and operations
  execution_mode: parallel
  specialist_ids:
    - discovery-agent
    - deployer-agent
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
tags: ['deployment', 'portainer', 'docker', 'stack', 'infrastructure']
concept: CONCEPT:INFRA-001
metadata:
  version: '1.2.1'
---

# Deploy Platform Stack Workflow

**CONCEPT:INFRA-001**

End-to-end deployment of an infrastructure platform using docker-compose files and Portainer MCP.

## Steps

### Step 0: Portainer Mcp
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Use portainer_environment to get the endpoint ID where the stack will be deployed.
Expected: `endpoint, id`

### Step 1: Portainer Mcp
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Use portainer_stack to create the standalone stack from the docker-compose file.
Expected: `stack, create`

### Step 2: KG Persistence [depends_on: portainer-mcp]
**Agent**: `deployer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Platform Stack results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Portainer Mcp; Step 1 — Portainer Mcp
- **After level 0:** Step 2 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
