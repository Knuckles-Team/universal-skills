---
name: employee_onboarding_pipeline
description: Parallel execution workflow for employee onboarding pipeline using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-microsoft
---

# Parallel Workflow: Employee Onboarding Pipeline

This workflow defines the topological parallel execution steps for employee onboarding pipeline.

## Steps

### Step 1: create_accounts
Execute the create accounts phase for the employee_onboarding_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: create_accounts_artifacts
### Step 2: setup_access [depends_on: create_accounts]
Execute the setup access phase for the employee_onboarding_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: setup_access_artifacts
### Step 3: assign_equipment [depends_on: setup_access]
Execute the assign equipment phase for the employee_onboarding_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: assign_equipment_artifacts
### Step 4: training_schedule [depends_on: assign_equipment]
Execute the training schedule phase for the employee_onboarding_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: training_schedule_artifacts
### Step 5: checklist [depends_on: training_schedule]
Execute the checklist phase for the employee_onboarding_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: checklist_artifacts
