---
name: agent_prompt_optimizer
description: Parallel execution workflow for agent prompt optimizer using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-langfuse
---

# Parallel Workflow: Agent Prompt Optimizer

This workflow defines the topological parallel execution steps for agent prompt optimizer.

## Steps

### Step 1: fan_out_per_prompt_benchmark
Execute the Fan-out per prompt: benchmark phase for the agent_prompt_optimizer workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_prompt_benchmark_artifacts
### Step 2: variant_generation [depends_on: fan_out_per_prompt_benchmark]
Execute the variant generation phase for the agent_prompt_optimizer workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: variant_generation_artifacts
### Step 3: a_b_eval [depends_on: variant_generation]
Execute the A/B eval phase for the agent_prompt_optimizer workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: a_b_eval_artifacts
### Step 4: select_best [depends_on: a_b_eval]
Execute the select best phase for the agent_prompt_optimizer workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: select_best_artifacts
