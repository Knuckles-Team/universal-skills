---
name: greenfield_project_scaffold
description: Parallel execution workflow for greenfield project scaffold using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-github-mcp
---

# Parallel Workflow: Greenfield Project Scaffold

This workflow defines the topological parallel execution steps for greenfield project scaffold.

## Steps

### Step 1: spec
Execute the spec phase for the greenfield_project_scaffold workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: spec_artifacts
### Step 2: architecture [depends_on: spec]
Execute the architecture phase for the greenfield_project_scaffold workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: architecture_artifacts
### Step 3: scaffold [depends_on: architecture]
Execute the scaffold phase for the greenfield_project_scaffold workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scaffold_artifacts
### Step 4: base_impl [depends_on: scaffold]
Execute the base impl phase for the greenfield_project_scaffold workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: base_impl_artifacts
### Step 5: ci_setup [depends_on: base_impl]
Execute the CI setup phase for the greenfield_project_scaffold workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: ci_setup_artifacts
### Step 6: docs [depends_on: ci_setup]
Execute the docs phase for the greenfield_project_scaffold workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: docs_artifacts
