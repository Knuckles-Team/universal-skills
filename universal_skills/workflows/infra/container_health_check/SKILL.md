---
name: container_health_check
description: Full Docker infrastructure health assessment. Lists containers, images, volumes, and networks, then retrieves logs from a running container.
domain: infrastructure
tags: ['docker', 'health', 'monitoring', 'containers']
requires: ['DOCKER_HOST', 'container-manager-mcp']
---

# container_health_check Workflow

Full Docker infrastructure health assessment. Lists containers, images, volumes, and networks, then retrieves logs from a running container.

### Step 0: container-manager-mcp
List all running containers and their current status
Expected: container, running, status

### Step 1: container-manager-mcp
List all Docker images with their sizes and tags
Expected: image, tag

### Step 2: container-manager-mcp
Show all Docker volumes and networks
Expected: volume, network
Depends On: Step 0, Step 1

### Step 3: container-manager-mcp
Get the logs for one of the running containers
Expected: log
Depends On: Step 0
