---
name: training_program_builder
description: Parallel execution workflow for training program builder using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-atlassian
---

# Parallel Workflow: Training Program Builder

This workflow defines the topological parallel execution steps for training program builder.

## Steps

### Step 1: skill_gap_analysis
Execute the skill gap analysis phase for the training_program_builder workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: skill_gap_analysis_artifacts
### Step 2: curate_content [depends_on: skill_gap_analysis]
Execute the curate content phase for the training_program_builder workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: curate_content_artifacts
### Step 3: build_curriculum [depends_on: curate_content]
Execute the build curriculum phase for the training_program_builder workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: build_curriculum_artifacts
### Step 4: schedule [depends_on: build_curriculum]
Execute the schedule phase for the training_program_builder workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: schedule_artifacts
### Step 5: track [depends_on: schedule]
Execute the track phase for the training_program_builder workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: track_artifacts
