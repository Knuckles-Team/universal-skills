---
name: deploy_log_aggregation
description: Parallel execution workflow for deploy log aggregation using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-portainer
---

# Parallel Workflow: Deploy Log Aggregation

This workflow defines the topological parallel execution steps for deploy log aggregation.

## Steps

### Step 1: vector
Execute the vector phase for the deploy_log_aggregation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: vector_artifacts
### Step 2: loki
Execute the loki phase for the deploy_log_aggregation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: loki_artifacts
### Step 3: grafana
Execute the grafana phase for the deploy_log_aggregation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: grafana_artifacts
### Step 4: alerting_rules [depends_on: vector, loki, grafana]
Execute the alerting rules phase for the deploy_log_aggregation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: alerting_rules_artifacts
