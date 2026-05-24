---
name: container_image_audit
description: Parallel execution workflow for container image audit using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-container-manager
---

# Parallel Workflow: Container Image Audit

This workflow defines the topological parallel execution steps for container image audit.

## Steps

### Step 1: list_images
Execute the list images phase for the container_image_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: list_images_artifacts
### Step 2: check_for_cves [depends_on: list_images]
Execute the check for CVEs phase for the container_image_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: check_for_cves_artifacts
### Step 3: prune_unused [depends_on: check_for_cves]
Execute the prune unused phase for the container_image_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: prune_unused_artifacts
### Step 4: report [depends_on: prune_unused]
Execute the report phase for the container_image_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
