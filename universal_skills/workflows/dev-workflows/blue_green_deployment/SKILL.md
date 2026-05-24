---
name: blue_green_deployment
description: Parallel execution workflow for blue green deployment using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-portainer
---

# Parallel Workflow: Blue Green Deployment

This workflow defines the topological parallel execution steps for blue green deployment.

## Steps

### Step 1: deploy_green
Execute the deploy green phase for the blue_green_deployment workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: deploy_green_artifacts
### Step 2: health_check [depends_on: deploy_green]
Execute the health check phase for the blue_green_deployment workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: health_check_artifacts
### Step 3: switch_traffic [depends_on: health_check]
Execute the switch traffic phase for the blue_green_deployment workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: switch_traffic_artifacts
### Step 4: drain_blue [depends_on: switch_traffic]
Execute the drain blue phase for the blue_green_deployment workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: drain_blue_artifacts
