---
name: api_breaking_change_migration
description: Parallel execution workflow for api breaking change migration using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Api Breaking Change Migration

This workflow defines the topological parallel execution steps for api breaking change migration.

## Steps

### Step 1: detect_breaking_changes
Execute the detect breaking changes phase for the api_breaking_change_migration workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: detect_breaking_changes_artifacts
### Step 2: find_all_consumers [depends_on: detect_breaking_changes]
Execute the find all consumers phase for the api_breaking_change_migration workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: find_all_consumers_artifacts
### Step 3: parallel_update [depends_on: find_all_consumers]
Execute the parallel update phase for the api_breaking_change_migration workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parallel_update_artifacts
### Step 4: test [depends_on: parallel_update]
Execute the test phase for the api_breaking_change_migration workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: test_artifacts
