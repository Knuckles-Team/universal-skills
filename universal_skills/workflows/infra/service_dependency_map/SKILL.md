---
name: service_dependency_map
description: Maps the full service dependency chain from MCP server to agent package to container to stack to host, creating a queryable dependency graph in the Knowledge Graph.
domain: infrastructure
tags: ['services', 'dependencies', 'mapping', 'mcp', 'topology']
requires: ['portainer-mcp', 'container-manager-mcp', 'graph-os']
---

# service_dependency_map Workflow

Maps the full service dependency chain from MCP server to agent package to container to stack to host, creating a queryable dependency graph in the Knowledge Graph.

### Step 0: portainer-mcp
List all stacks and their containers with service labels and network attachments
Expected: stack, container, label

### Step 1: container-manager-mcp
Inspect each container for Traefik labels, health checks, and inter-service dependencies
Expected: traefik, label, health
Depends On: Step 0

### Step 2: graph-os
Build the full dependency graph: MCPServer -[DEPLOYED_ON]-> Container -[BELONGS_TO_STACK]-> ContainerStack -[RUNS_ON]-> HardwareNode, and ProxyRoute -[ROUTES_TO]-> PlatformService
Expected: dependency, graph, relationship
Depends On: Step 1
