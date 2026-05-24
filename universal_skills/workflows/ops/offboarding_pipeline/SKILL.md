---
name: offboarding_pipeline
description: Parallel execution workflow for offboarding pipeline using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-microsoft
---

# Parallel Workflow: Offboarding Pipeline

This workflow defines the topological parallel execution steps for offboarding pipeline.

## Steps

### Step 1: revoke_access
Execute the revoke access phase for the offboarding_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: revoke_access_artifacts
### Step 2: collect_equipment [depends_on: revoke_access]
Execute the collect equipment phase for the offboarding_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: collect_equipment_artifacts
### Step 3: knowledge_transfer [depends_on: collect_equipment]
Execute the knowledge transfer phase for the offboarding_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: knowledge_transfer_artifacts
### Step 4: exit_interview [depends_on: knowledge_transfer]
Execute the exit interview phase for the offboarding_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: exit_interview_artifacts
