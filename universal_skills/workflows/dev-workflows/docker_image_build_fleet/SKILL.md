---
name: docker_image_build_fleet
description: Parallel execution workflow for docker image build fleet using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-container-manager
---

# Parallel Workflow: Docker Image Build Fleet

This workflow defines the topological parallel execution steps for docker image build fleet.

## Steps

### Step 1: build
Execute the build phase for the docker_image_build_fleet workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: build_artifacts
### Step 2: scan [depends_on: build]
Execute the scan phase for the docker_image_build_fleet workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scan_artifacts
### Step 3: push [depends_on: scan]
Execute the push phase for the docker_image_build_fleet workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: push_artifacts
### Step 4: update_stack [depends_on: push]
Execute the update stack phase for the docker_image_build_fleet workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: update_stack_artifacts
