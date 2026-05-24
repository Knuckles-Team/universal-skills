---
name: deploy_dev_environment
description: Parallel execution workflow for deploy dev environment using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-portainer
---

# Parallel Workflow: Deploy Dev Environment

This workflow defines the topological parallel execution steps for deploy dev environment.

## Steps

### Step 1: gitea_gitlab
Execute the gitea/gitlab phase for the deploy_dev_environment workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: gitea_gitlab_artifacts
### Step 2: registry
Execute the registry phase for the deploy_dev_environment workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: registry_artifacts
### Step 3: runner
Execute the runner phase for the deploy_dev_environment workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: runner_artifacts
### Step 4: ci_pipeline [depends_on: gitea_gitlab, registry, runner]
Execute the CI pipeline phase for the deploy_dev_environment workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: ci_pipeline_artifacts
