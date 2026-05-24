---
name: annual_technology_review
description: Parallel execution workflow for annual technology review using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-searxng
---

# Parallel Workflow: Annual Technology Review

This workflow defines the topological parallel execution steps for annual technology review.

## Steps

### Step 1: evaluate
Execute the evaluate phase for the annual_technology_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: evaluate_artifacts
### Step 2: compare_alternatives [depends_on: evaluate]
Execute the compare alternatives phase for the annual_technology_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: compare_alternatives_artifacts
### Step 3: migration_plan [depends_on: compare_alternatives]
Execute the migration plan phase for the annual_technology_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: migration_plan_artifacts
