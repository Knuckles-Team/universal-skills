---
name: feature_development_pipeline
description: Parallel execution workflow for feature development pipeline using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-github-mcp
---

# Parallel Workflow: Feature Development Pipeline

This workflow defines the topological parallel execution steps for feature development pipeline.

## Steps

### Step 1: spec
Execute the spec phase for the feature_development_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: spec_artifacts
### Step 2: plan [depends_on: spec]
Execute the plan phase for the feature_development_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: plan_artifacts
### Step 3: parallel_impl_py [depends_on: plan]
Execute the parallel impl (py phase for the feature_development_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parallel_impl_py_artifacts
### Step 4: ts [depends_on: plan]
Execute the ts phase for the feature_development_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: ts_artifacts
### Step 5: tests [depends_on: plan]
Execute the tests) phase for the feature_development_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: tests_artifacts
### Step 6: review [depends_on: parallel_impl_py, ts, tests]
Execute the review phase for the feature_development_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: review_artifacts
### Step 7: merge [depends_on: review]
Execute the merge phase for the feature_development_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: merge_artifacts
