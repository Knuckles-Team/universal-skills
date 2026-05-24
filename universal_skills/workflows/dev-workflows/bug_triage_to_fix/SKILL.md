---
name: bug_triage_to_fix
description: Parallel execution workflow for bug triage to fix using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-github-mcp
---

# Parallel Workflow: Bug Triage To Fix

This workflow defines the topological parallel execution steps for bug triage to fix.

## Steps

### Step 1: triage
Execute the triage phase for the bug_triage_to_fix workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: triage_artifacts
### Step 2: reproduce [depends_on: triage]
Execute the reproduce phase for the bug_triage_to_fix workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: reproduce_artifacts
### Step 3: diagnose [depends_on: reproduce]
Execute the diagnose phase for the bug_triage_to_fix workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: diagnose_artifacts
### Step 4: fix [depends_on: diagnose]
Execute the fix phase for the bug_triage_to_fix workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fix_artifacts
### Step 5: test [depends_on: fix]
Execute the test phase for the bug_triage_to_fix workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: test_artifacts
### Step 6: pr [depends_on: test]
Execute the PR phase for the bug_triage_to_fix workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pr_artifacts
