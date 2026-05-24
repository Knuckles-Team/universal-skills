---
name: multi_repo_refactor
description: Parallel execution workflow for multi repo refactor using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Multi Repo Refactor

This workflow defines the topological parallel execution steps for multi repo refactor.

## Steps

### Step 1: analyze
Execute the analyze phase for the multi_repo_refactor workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: analyze_artifacts
### Step 2: refactor [depends_on: analyze]
Execute the refactor phase for the multi_repo_refactor workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: refactor_artifacts
### Step 3: test [depends_on: refactor]
Execute the test phase for the multi_repo_refactor workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: test_artifacts
### Step 4: pr [depends_on: test]
Execute the PR phase for the multi_repo_refactor workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pr_artifacts
