---
name: dependency_update_sweep
description: Parallel execution workflow for dependency update sweep using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Dependency Update Sweep

This workflow defines the topological parallel execution steps for dependency update sweep.

## Steps

### Step 1: check_outdated
Execute the check outdated phase for the dependency_update_sweep workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: check_outdated_artifacts
### Step 2: update [depends_on: check_outdated]
Execute the update phase for the dependency_update_sweep workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: update_artifacts
### Step 3: test [depends_on: update]
Execute the test phase for the dependency_update_sweep workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: test_artifacts
### Step 4: pr [depends_on: test]
Execute the PR phase for the dependency_update_sweep workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pr_artifacts
