---
name: feature-development-pipeline
skill_type: workflow
description: Parallel execution workflow for feature development pipeline using the Unified Parallel Engine
domain: development-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-github-mcp
metadata:
  version: '1.0.2'
---

# Parallel Workflow: Feature Development Pipeline

This workflow defines the topological parallel execution steps for feature development pipeline.

## Steps

### Step 1: spec
Execute the spec phase for the feature-development-pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: spec_artifacts
### Step 2: plan [depends_on: spec]
Execute the plan phase for the feature-development-pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: plan_artifacts
### Step 3: parallel_impl_py [depends_on: plan]
Execute the parallel impl (py phase for the feature-development-pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parallel_impl_py_artifacts
### Step 4: ts [depends_on: plan]
Execute the ts phase for the feature-development-pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: ts_artifacts
### Step 5: tests [depends_on: plan]
Execute the tests) phase for the feature-development-pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: tests_artifacts
### Step 6: review [depends_on: parallel_impl_py, ts, tests]
Execute the review phase for the feature-development-pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: review_artifacts
### Step 7: merge [depends_on: review]
Execute the merge phase for the feature-development-pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: merge_artifacts

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — spec
- **After level 0:** Step 2 — plan
- **After level 1:** Step 3 — parallel_impl_py; Step 4 — ts; Step 5 — tests
- **After level 2:** Step 6 — review
- **After level 3:** Step 7 — merge

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
