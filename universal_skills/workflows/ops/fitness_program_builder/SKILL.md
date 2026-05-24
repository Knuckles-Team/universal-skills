---
name: fitness_program_builder
description: Parallel execution workflow for fitness program builder using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-wger
---

# Parallel Workflow: Fitness Program Builder

This workflow defines the topological parallel execution steps for fitness program builder.

## Steps

### Step 1: assess_goals
Execute the assess goals phase for the fitness_program_builder workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: assess_goals_artifacts
### Step 2: select_exercises [depends_on: assess_goals]
Execute the select exercises phase for the fitness_program_builder workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: select_exercises_artifacts
### Step 3: build_routine [depends_on: select_exercises]
Execute the build routine phase for the fitness_program_builder workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: build_routine_artifacts
### Step 4: schedule [depends_on: build_routine]
Execute the schedule phase for the fitness_program_builder workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: schedule_artifacts
### Step 5: track [depends_on: schedule]
Execute the track phase for the fitness_program_builder workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: track_artifacts
