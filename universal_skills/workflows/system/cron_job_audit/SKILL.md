---
name: cron_job_audit
description: Parallel execution workflow for cron job audit using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-systems-manager
---

# Parallel Workflow: Cron Job Audit

This workflow defines the topological parallel execution steps for cron job audit.

## Steps

### Step 1: fan_out_per_host_list_crontabs
Execute the Fan-out per host: list crontabs phase for the cron_job_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_host_list_crontabs_artifacts
### Step 2: classify [depends_on: fan_out_per_host_list_crontabs]
Execute the classify phase for the cron_job_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: classify_artifacts
### Step 3: find_overlaps [depends_on: classify]
Execute the find overlaps phase for the cron_job_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: find_overlaps_artifacts
### Step 4: optimize [depends_on: find_overlaps]
Execute the optimize phase for the cron_job_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: optimize_artifacts
