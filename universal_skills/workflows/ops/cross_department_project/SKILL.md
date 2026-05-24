---
name: cross_department_project
description: Parallel execution workflow for cross department project using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-multiple
---

# Parallel Workflow: Cross Department Project

This workflow defines the topological parallel execution steps for cross department project.

## Steps

### Step 1: phase_1_research_parallel
Execute the phase 1 research parallel phase for the cross_department_project workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: phase_1_research_parallel_artifacts
### Step 2: phase_2_impl_parallel [depends_on: phase_1_research_parallel]
Execute the phase 2 impl parallel phase for the cross_department_project workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: phase_2_impl_parallel_artifacts
### Step 3: phase_3_qa [depends_on: phase_2_impl_parallel]
Execute the phase 3 qa phase for the cross_department_project workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: phase_3_qa_artifacts
