---
name: deploy_media_stack
description: Parallel execution workflow for deploy media stack using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-portainer
---

# Parallel Workflow: Deploy Media Stack

This workflow defines the topological parallel execution steps for deploy media stack.

## Steps

### Step 1: jellyfin
Execute the jellyfin phase for the deploy_media_stack workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: jellyfin_artifacts
### Step 2: sonarr
Execute the sonarr phase for the deploy_media_stack workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: sonarr_artifacts
### Step 3: radarr
Execute the radarr phase for the deploy_media_stack workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: radarr_artifacts
### Step 4: prowlarr
Execute the prowlarr phase for the deploy_media_stack workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: prowlarr_artifacts
### Step 5: bazarr [depends_on: jellyfin, sonarr, radarr, prowlarr]
Execute the bazarr phase for the deploy_media_stack workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: bazarr_artifacts
