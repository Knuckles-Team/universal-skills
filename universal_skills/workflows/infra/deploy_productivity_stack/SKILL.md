---
name: deploy_productivity_stack
description: Parallel execution workflow for deploy productivity stack using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-portainer
---

# Parallel Workflow: Deploy Productivity Stack

This workflow defines the topological parallel execution steps for deploy productivity stack.

## Steps

### Step 1: nextcloud
Execute the nextcloud phase for the deploy_productivity_stack workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: nextcloud_artifacts
### Step 2: mealie
Execute the mealie phase for the deploy_productivity_stack workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: mealie_artifacts
### Step 3: listmonk
Execute the listmonk phase for the deploy_productivity_stack workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: listmonk_artifacts
### Step 4: dns_rewrites [depends_on: nextcloud, mealie, listmonk]
Execute the DNS rewrites phase for the deploy_productivity_stack workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: dns_rewrites_artifacts
