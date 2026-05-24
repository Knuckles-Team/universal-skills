---
name: overnight_code_improvement
description: Parallel execution workflow for overnight code improvement using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-github-mcp
---

# Parallel Workflow: Overnight Code Improvement

This workflow defines the topological parallel execution steps for overnight code improvement.

## Steps

### Step 1: audit
Execute the audit phase for the overnight_code_improvement workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: audit_artifacts
### Step 2: enhance [depends_on: audit]
Execute the enhance phase for the overnight_code_improvement workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: enhance_artifacts
### Step 3: test [depends_on: enhance]
Execute the test phase for the overnight_code_improvement workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: test_artifacts
### Step 4: pr [depends_on: test]
Execute the PR phase for the overnight_code_improvement workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pr_artifacts
### Step 5: report [depends_on: pr]
Execute the report phase for the overnight_code_improvement workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
