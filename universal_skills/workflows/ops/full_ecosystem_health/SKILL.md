---
name: full_ecosystem_health
description: End-to-end ecosystem health check across containers, system resources, workspace, and observability stack. This is the "canary" workflow that validates all infrastructure layers are operational.
domain: operations
tags: ['ecosystem', 'health', 'canary', 'full-stack']
requires: ['container-manager-mcp', 'systems-manager', 'langfuse-mcp', 'repository-manager-mcp']
---

# full_ecosystem_health Workflow

End-to-end ecosystem health check across containers, system resources, workspace, and observability stack. This is the "canary" workflow that validates all infrastructure layers are operational.

### Step 0: systems-manager
Get system memory, CPU, and disk stats
Expected: memory, cpu

### Step 1: container-manager-mcp
List all running Docker containers and their health status
Expected: container, running

### Step 2: langfuse-mcp
Check Langfuse health and list recent traces
Expected: health

### Step 3: repository-manager-mcp
List workspace actions and verify workspace configuration
Expected: workspace, list
