---
name: helm_chart_release
description: Parallel execution workflow for helm chart release using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-portainer
---

# Parallel Workflow: Helm Chart Release

This workflow defines the topological parallel execution steps for helm chart release.

## Steps

### Step 1: lint
Execute the lint phase for the helm_chart_release workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: lint_artifacts
### Step 2: template [depends_on: lint]
Execute the template phase for the helm_chart_release workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: template_artifacts
### Step 3: package [depends_on: template]
Execute the package phase for the helm_chart_release workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: package_artifacts
### Step 4: push [depends_on: package]
Execute the push phase for the helm_chart_release workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: push_artifacts
### Step 5: deploy [depends_on: push]
Execute the deploy phase for the helm_chart_release workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: deploy_artifacts
### Step 6: verify [depends_on: deploy]
Execute the verify phase for the helm_chart_release workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: verify_artifacts
