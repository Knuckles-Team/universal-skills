---
name: readme_standardization
description: Parallel execution workflow for readme standardization using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Readme Standardization

This workflow defines the topological parallel execution steps for readme standardization.

## Steps

### Step 1: audit_readme
Execute the audit README phase for the readme_standardization workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: audit_readme_artifacts
### Step 2: update_format [depends_on: audit_readme]
Execute the update format phase for the readme_standardization workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: update_format_artifacts
### Step 3: add_badges [depends_on: update_format]
Execute the add badges phase for the readme_standardization workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: add_badges_artifacts
### Step 4: pr [depends_on: add_badges]
Execute the PR phase for the readme_standardization workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pr_artifacts
