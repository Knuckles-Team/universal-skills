---
name: system_observability_sweep
description: Cross-system health and resource check combining system metrics with Langfuse observability status.
domain: infrastructure
tags: ['monitoring', 'health', 'cross-system', 'observability']
requires: ['systems-manager', 'langfuse-mcp']
---

# system_observability_sweep Workflow

Cross-system health and resource check combining system metrics with Langfuse observability status.

### Step 0: systems-manager
Get the system memory usage, CPU stats, and disk utilization
Expected: memory, cpu

### Step 1: langfuse-mcp
Check the Langfuse health endpoint and list all current datasets
Expected: health, dataset

### Step 2: langfuse-mcp
List the most recent traces and their status
Expected: trace
Depends On: Step 1
