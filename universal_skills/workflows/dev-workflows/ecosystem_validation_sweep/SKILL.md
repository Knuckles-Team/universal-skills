---
name: ecosystem_validation_sweep
description: Parallel execution workflow for ecosystem validation sweep using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Ecosystem Validation Sweep

This workflow defines the topological parallel execution steps for ecosystem validation sweep.

## Steps

### Step 1: install
Execute the install phase for the ecosystem_validation_sweep workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: install_artifacts
### Step 2: lint [depends_on: install]
Execute the lint phase for the ecosystem_validation_sweep workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: lint_artifacts
### Step 3: test [depends_on: lint]
Execute the test phase for the ecosystem_validation_sweep workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: test_artifacts
### Step 4: report [depends_on: test]
Execute the report phase for the ecosystem_validation_sweep workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
