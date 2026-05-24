---
name: performance_benchmark_suite
description: Parallel execution workflow for performance benchmark suite using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-data-science
---

# Parallel Workflow: Performance Benchmark Suite

This workflow defines the topological parallel execution steps for performance benchmark suite.

## Steps

### Step 1: profile
Execute the profile phase for the performance_benchmark_suite workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: profile_artifacts
### Step 2: identify_bottlenecks [depends_on: profile]
Execute the identify bottlenecks phase for the performance_benchmark_suite workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: identify_bottlenecks_artifacts
### Step 3: optimize [depends_on: identify_bottlenecks]
Execute the optimize phase for the performance_benchmark_suite workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: optimize_artifacts
### Step 4: benchmark [depends_on: optimize]
Execute the benchmark phase for the performance_benchmark_suite workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: benchmark_artifacts
