---
name: portainer_stack_troubleshooter
description: Identifies stopped or unhealthy containers inside Portainer stacks, aggregates logs, and creates a step-by-step resolution plan using portainer-agent and tunnel-manager.
domain: infra
tags: ['portainer', 'stacks', 'docker', 'troubleshooting', 'portainer-agent', 'tunnel-manager']
requires: ['portainer-agent']
---

# portainer_stack_troubleshooter Workflow

Identifies stopped or unhealthy containers inside Portainer stacks, aggregates logs, and creates a step-by-step resolution plan using portainer-agent and tunnel-manager.

### Step 0: portainer-agent
Retrieve active stacks list using portainer_stack get_stacks tool, and retrieve the full list of running and stopped containers using portainer_docker docker_list_containers tool.
Expected: portainer_stacks, containers_status

### Step 1: user-interaction
Scan containers_status to isolate unhealthy, degraded, or stopped instances. Construct a visual status dashboard highlighting failed stacks and down services.
Expected: stack_triage_dashboard
Depends On: Step 0

### Step 2: portainer-agent
For the identified failed containers, fetch the diagnostic logs using portainer_docker docker_get_container_logs tool. Suggest precise stack-level updates or restart commands.
Expected: container_diagnostics, resolution_plan
Depends On: Step 1
