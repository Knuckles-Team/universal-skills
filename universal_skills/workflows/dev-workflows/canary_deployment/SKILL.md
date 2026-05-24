---
name: canary_deployment
description: Parallel execution workflow for canary deployment using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-portainer
---

# Parallel Workflow: Canary Deployment

This workflow defines the topological parallel execution steps for canary deployment.

## Steps

### Step 1: deploy_canary
Execute the deploy canary phase for the canary_deployment workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: deploy_canary_artifacts
### Step 2: monitor_metrics [depends_on: deploy_canary]
Execute the monitor metrics phase for the canary_deployment workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: monitor_metrics_artifacts
### Step 3: compare_to_baseline [depends_on: monitor_metrics]
Execute the compare to baseline phase for the canary_deployment workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: compare_to_baseline_artifacts
### Step 4: promote_rollback [depends_on: compare_to_baseline]
Execute the promote/rollback phase for the canary_deployment workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: promote_rollback_artifacts
