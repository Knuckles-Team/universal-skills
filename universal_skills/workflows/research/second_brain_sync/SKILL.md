---
name: second_brain_sync
description: Parallel execution workflow for second brain sync using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-nextcloud
---

# Parallel Workflow: Second Brain Sync

This workflow defines the topological parallel execution steps for second brain sync.

## Steps

### Step 1: obsidian
Execute the obsidian phase for the second_brain_sync workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: obsidian_artifacts
### Step 2: nextcloud
Execute the nextcloud phase for the second_brain_sync workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: nextcloud_artifacts
### Step 3: kg
Execute the KG phase for the second_brain_sync workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: kg_artifacts
### Step 4: bidirectional_sync [depends_on: obsidian, nextcloud, kg]
Execute the bidirectional sync phase for the second_brain_sync workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: bidirectional_sync_artifacts
### Step 5: dedup [depends_on: bidirectional_sync]
Execute the dedup phase for the second_brain_sync workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: dedup_artifacts
