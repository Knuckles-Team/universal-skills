---
name: type_coverage_campaign
description: Parallel execution workflow for type coverage campaign using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Type Coverage Campaign

This workflow defines the topological parallel execution steps for type coverage campaign.

## Steps

### Step 1: pyright_mypy_analysis
Execute the pyright/mypy analysis phase for the type_coverage_campaign workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pyright_mypy_analysis_artifacts
### Step 2: add_types [depends_on: pyright_mypy_analysis]
Execute the add types phase for the type_coverage_campaign workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: add_types_artifacts
### Step 3: test [depends_on: add_types]
Execute the test phase for the type_coverage_campaign workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: test_artifacts
### Step 4: pr [depends_on: test]
Execute the PR phase for the type_coverage_campaign workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pr_artifacts
