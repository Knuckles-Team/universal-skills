---
name: local_container_troubleshooter
description: Automatically scans local containers, pulls crash logs, and designs remediation steps to resolve failures using container-manager-mcp.
domain: infra
tags: ['docker', 'podman', 'local-deploy', 'troubleshooting', 'container-manager-mcp']
requires: ['container-manager-mcp']
---

# local_container_troubleshooter Workflow

Automatically scans local containers, pulls crash logs, and designs remediation steps to resolve failures using container-manager-mcp.

### Step 0: container-manager-mcp
Scan all local container instances (running and stopped) using cm_container_operations list_containers tool with all_containers parameter.
Expected: local_containers_list

### Step 1: user-interaction
Filter and present any stopped or unhealthy containers from local_containers_list. Ask the user for confirmation to inspect crash logs.
Expected: selected_containers

### Step 2: container-manager-mcp
Retrieve log outputs for selected failed containers using cm_container_operations get_container_logs tool with tail parameter, and check local compose environments using cm_compose_operations ps tool.
Expected: container_logs, compose_states
Depends On: Step 1
