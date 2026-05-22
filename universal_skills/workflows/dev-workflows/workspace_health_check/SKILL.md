---
name: workspace_health_check
description: Combined workspace + system health validation. Checks repository state alongside system resources.
domain: development
tags: ['workspace', 'health', 'systems', 'cross-domain']
requires: ['repository-manager-mcp', 'systems-manager']
---

# workspace_health_check Workflow

Combined workspace + system health validation. Checks repository state alongside system resources.

### Step 0: repository-manager-mcp
List the available workspace actions and current workspace configuration
Expected: workspace, list

### Step 1: systems-manager
Get current system memory and CPU utilization
Expected: memory, cpu

### Step 2: systems-manager
Check disk usage for the main workspace partition
Expected: disk, usage
Depends On: Step 1
