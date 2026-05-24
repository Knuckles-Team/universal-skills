---
name: pr_review_swarm
description: Parallel execution workflow for pr review swarm using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-github-mcp
---

# Parallel Workflow: Pr Review Swarm

This workflow defines the topological parallel execution steps for pr review swarm.

## Steps

### Step 1: security
Execute the security phase for the pr_review_swarm workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: security_artifacts
### Step 2: performance
Execute the performance phase for the pr_review_swarm workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: performance_artifacts
### Step 3: style
Execute the style phase for the pr_review_swarm workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: style_artifacts
### Step 4: correctness
Execute the correctness phase for the pr_review_swarm workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: correctness_artifacts
### Step 5: test_coverage
Execute the test coverage phase for the pr_review_swarm workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: test_coverage_artifacts
### Step 6: merge_decision [depends_on: security, performance, style, correctness, test_coverage]
Execute the merge decision phase for the pr_review_swarm workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: merge_decision_artifacts
