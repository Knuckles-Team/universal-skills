---
name: local_container_troubleshooter
description: >-
  Automatically scans local containers, pulls crash logs, and designs remediation steps to resolve failures using container-manager-mcp.
domain: infra
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
---

# Local Container Troubleshooter Workflow

**CONCEPT:INFRA-001**

Automatically scans local containers, pulls crash logs, and designs remediation steps to resolve failures using container-manager-mcp.

## Steps

### Step 0: Container Manager Mcp
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Scan all local container instances (running and stopped) using cm_container_operations list_containers tool with all_containers parameter.
Expected: `local_containers_list`

### Step 1: User Interaction
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Filter and present any stopped or unhealthy containers from local_containers_list. Ask the user for confirmation to inspect crash logs.
Expected: `selected_containers`

### Step 2: Container Manager Mcp
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Retrieve log outputs for selected failed containers using cm_container_operations get_container_logs tool with tail parameter.
Expected: `container_logs`

### Step 3: Container Manager Mcp
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Check local compose environments using cm_compose_operations ps tool.
Expected: `compose_states`

### Step 4: User Interaction
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Fuse container logs and compose states to diagnose root failures and formulate automated remediation steps.
Expected: `remediation_plan`

### Step 5: KG Persistence [depends_on: user-interaction]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Local Container Troubleshooter results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
