---
name: monorepo_release_pipeline
description: Parallel execution workflow for monorepo release pipeline using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Monorepo Release Pipeline

This workflow defines the topological parallel execution steps for monorepo release pipeline.

## Steps

### Step 1: version_bump
Execute the version bump phase for the monorepo_release_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: version_bump_artifacts
### Step 2: changelog [depends_on: version_bump]
Execute the changelog phase for the monorepo_release_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: changelog_artifacts
### Step 3: parallel_build_per_package [depends_on: changelog]
Execute the parallel build per package phase for the monorepo_release_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parallel_build_per_package_artifacts
### Step 4: publish [depends_on: parallel_build_per_package]
Execute the publish phase for the monorepo_release_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: publish_artifacts
### Step 5: tag [depends_on: publish]
Execute the tag phase for the monorepo_release_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: tag_artifacts
