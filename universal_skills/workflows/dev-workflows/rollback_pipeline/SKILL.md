---
name: rollback_pipeline
description: Parallel execution workflow for rollback pipeline using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-portainer
---

# Parallel Workflow: Rollback Pipeline

This workflow defines the topological parallel execution steps for rollback pipeline.

## Steps

### Step 1: detect_failure
Execute the detect failure phase for the rollback_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: detect_failure_artifacts
### Step 2: identify_last_good [depends_on: detect_failure]
Execute the identify last good phase for the rollback_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: identify_last_good_artifacts
### Step 3: revert [depends_on: identify_last_good]
Execute the revert phase for the rollback_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: revert_artifacts
### Step 4: verify [depends_on: revert]
Execute the verify phase for the rollback_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: verify_artifacts
### Step 5: notify [depends_on: verify]
Execute the notify phase for the rollback_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: notify_artifacts
