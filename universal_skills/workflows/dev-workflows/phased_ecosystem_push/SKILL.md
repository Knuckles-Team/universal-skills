---
name: phased_ecosystem_push
description: Parallel execution workflow for phased ecosystem push using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Phased Ecosystem Push

This workflow defines the topological parallel execution steps for phased ecosystem push.

## Steps

### Step 1: wave_per_phase_bump
Execute the Wave per phase: bump phase for the phased_ecosystem_push workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: wave_per_phase_bump_artifacts
### Step 2: commit [depends_on: wave_per_phase_bump]
Execute the commit phase for the phased_ecosystem_push workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: commit_artifacts
### Step 3: push [depends_on: commit]
Execute the push phase for the phased_ecosystem_push workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: push_artifacts
### Step 4: verify_ci [depends_on: push]
Execute the verify CI phase for the phased_ecosystem_push workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: verify_ci_artifacts
### Step 5: next_phase [depends_on: verify_ci]
Execute the next phase phase for the phased_ecosystem_push workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: next_phase_artifacts
