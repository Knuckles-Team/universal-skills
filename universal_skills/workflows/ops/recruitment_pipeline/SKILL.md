---
name: recruitment_pipeline
description: Parallel execution workflow for recruitment pipeline using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-microsoft
---

# Parallel Workflow: Recruitment Pipeline

This workflow defines the topological parallel execution steps for recruitment pipeline.

## Steps

### Step 1: post_job
Execute the post job phase for the recruitment_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: post_job_artifacts
### Step 2: screen_resumes [depends_on: post_job]
Execute the screen resumes phase for the recruitment_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: screen_resumes_artifacts
### Step 3: schedule_interviews [depends_on: screen_resumes]
Execute the schedule interviews phase for the recruitment_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: schedule_interviews_artifacts
### Step 4: evaluate [depends_on: schedule_interviews]
Execute the evaluate phase for the recruitment_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: evaluate_artifacts
### Step 5: offer [depends_on: evaluate]
Execute the offer phase for the recruitment_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: offer_artifacts
