---
name: service_dependency_map
description: >-
  Maps the full service dependency chain from MCP server to agent package to container to stack to host, creating a queryable dependency graph in the Knowledge Graph.
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
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
    verifier-agent: [pt_docker, cnt_cm_container_operations]
tags: ['services', 'dependencies', 'mapping', 'mcp', 'topology']
concept: CONCEPT:INFRA-001
---

# Service Dependency Map Workflow

**CONCEPT:INFRA-001**

Maps the full service dependency chain from MCP server to agent package to container to stack to host, creating a queryable dependency graph in the Knowledge Graph.

## Steps

### Step 0: Portainer Mcp
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

List all stacks and their containers with service labels and network attachments
Expected: `stack, container, label`

### Step 1: Container Manager Mcp
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Inspect each container for Traefik labels, health checks, and inter-service dependencies
Expected: `traefik, label, health`

### Step 2: Graph Os
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Build the full dependency graph: MCPServer -[DEPLOYED_ON]-> Container -[BELONGS_TO_STACK]-> ContainerStack -[RUNS_ON]-> HardwareNode, and ProxyRoute -[ROUTES_TO]-> PlatformService
Expected: `dependency, graph, relationship`

### Step 3: KG Persistence [depends_on: graph-os]
**Agent**: `verifier-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Service Dependency Map results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
