---
name: agent_benchmark_suite
description: Parallel execution workflow for agent benchmark suite using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-langfuse
---

# Parallel Workflow: Agent Benchmark Suite

This workflow defines the topological parallel execution steps for agent benchmark suite.

## Steps

### Step 1: fan_out_per_agent_standardized_task
Execute the Fan-out per agent: standardized task phase for the agent_benchmark_suite workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_agent_standardized_task_artifacts
### Step 2: measure_latency [depends_on: fan_out_per_agent_standardized_task]
Execute the measure latency phase for the agent_benchmark_suite workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: measure_latency_artifacts
### Step 3: quality [depends_on: fan_out_per_agent_standardized_task]
Execute the quality phase for the agent_benchmark_suite workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: quality_artifacts
### Step 4: cost [depends_on: fan_out_per_agent_standardized_task]
Execute the cost phase for the agent_benchmark_suite workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: cost_artifacts
### Step 5: leaderboard [depends_on: measure_latency, quality, cost]
Execute the leaderboard phase for the agent_benchmark_suite workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: leaderboard_artifacts
