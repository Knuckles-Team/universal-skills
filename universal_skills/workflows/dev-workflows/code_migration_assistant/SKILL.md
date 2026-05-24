---
name: code_migration_assistant
description: Parallel execution workflow for code migration assistant using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-github-mcp
---

# Parallel Workflow: Code Migration Assistant

This workflow defines the topological parallel execution steps for code migration assistant.

## Steps

### Step 1: analyze_source
Execute the analyze source phase for the code_migration_assistant workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: analyze_source_artifacts
### Step 2: plan_migration [depends_on: analyze_source]
Execute the plan migration phase for the code_migration_assistant workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: plan_migration_artifacts
### Step 3: parallel_convert [depends_on: plan_migration]
Execute the parallel convert phase for the code_migration_assistant workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parallel_convert_artifacts
### Step 4: test [depends_on: parallel_convert]
Execute the test phase for the code_migration_assistant workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: test_artifacts
### Step 5: validate [depends_on: test]
Execute the validate phase for the code_migration_assistant workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: validate_artifacts
