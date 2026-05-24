---
name: dead_code_elimination
description: Parallel execution workflow for dead code elimination using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Dead Code Elimination

This workflow defines the topological parallel execution steps for dead code elimination.

## Steps

### Step 1: ast_analysis
Execute the AST analysis phase for the dead_code_elimination workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: ast_analysis_artifacts
### Step 2: unused_imports [depends_on: ast_analysis]
Execute the unused imports phase for the dead_code_elimination workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: unused_imports_artifacts
### Step 3: unreachable_code [depends_on: unused_imports]
Execute the unreachable code phase for the dead_code_elimination workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: unreachable_code_artifacts
### Step 4: pr [depends_on: unreachable_code]
Execute the PR phase for the dead_code_elimination workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pr_artifacts
