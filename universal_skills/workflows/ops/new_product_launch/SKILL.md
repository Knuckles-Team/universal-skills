---
name: new_product_launch
description: Parallel execution workflow for new product launch using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-multiple
---

# Parallel Workflow: New Product Launch

This workflow defines the topological parallel execution steps for new product launch.

## Steps

### Step 1: research
Execute the research phase for the new_product_launch workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: research_artifacts
### Step 2: engineering [depends_on: research]
Execute the engineering phase for the new_product_launch workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: engineering_artifacts
### Step 3: marketing [depends_on: research]
Execute the marketing phase for the new_product_launch workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: marketing_artifacts
### Step 4: legal_parallel [depends_on: research]
Execute the legal parallel phase for the new_product_launch workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: legal_parallel_artifacts
### Step 5: launch [depends_on: engineering, marketing, legal_parallel]
Execute the launch phase for the new_product_launch workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: launch_artifacts
