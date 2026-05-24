---
name: resource_usage_forecast
description: Parallel execution workflow for resource usage forecast using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-systems-manager
---

# Parallel Workflow: Resource Usage Forecast

This workflow defines the topological parallel execution steps for resource usage forecast.

## Steps

### Step 1: collect_cpu_mem_disk_per_host
Execute the collect CPU/mem/disk per host phase for the resource_usage_forecast workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: collect_cpu_mem_disk_per_host_artifacts
### Step 2: trend_analysis [depends_on: collect_cpu_mem_disk_per_host]
Execute the trend analysis phase for the resource_usage_forecast workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: trend_analysis_artifacts
### Step 3: capacity_report [depends_on: trend_analysis]
Execute the capacity report phase for the resource_usage_forecast workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: capacity_report_artifacts
