---
name: container-health-check
description: >-
  Full Docker infrastructure health assessment.
  Lists containers, images, volumes, and networks,
  then retrieves logs from a running container.
tags: [infrastructure, docker, health, monitoring, containers]
metadata:
  author: agent-utilities
  version: '1.0.0'
---
# Container Health Check Workflow

> [!NOTE]
> This workflow was migrated from the legacy WorkflowBundle preset system.

## Workflow Execution Steps

### Step 1: container-manager-mcp
List all running containers and their current status

### Step 2: container-manager-mcp
List all Docker images with their sizes and tags

### Step 3: container-manager-mcp
Show all Docker volumes and networks

### Step 4: container-manager-mcp
Get the logs for one of the running containers
