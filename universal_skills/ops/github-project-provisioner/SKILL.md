---
name: github-project-provisioner
description: Provisions and configures a new or existing GitHub project using standard default settings. Use this skill when asked to create a new project, provision a repository, or set up GitHub Actions pipelines and GitHub Pages.
license: MIT
tags: [github, provision, ci-cd, actions, pages, ops]
metadata:
  author: Genius
  version: '0.1.21'
---

# GitHub Project Provisioner

## Overview

This skill provisions a GitHub repository with standard CI/CD and deployment configurations. It handles creating the repository using the `github-agent` MCP tool, setting up standardized GitHub Actions workflows (with remote caching), and programmatically enabling GitHub Pages (via GitHub Actions workflow).

## Prerequisites
- The environment must provide `GITHUB_ACCESS_TOKEN` for the python scripts to authenticate. The `github-agent` MCP should already be available and configured with its own secrets. Do NOT hardcode or ask for secrets.

## Workflow

Follow these steps precisely:

### Step 1: Create or Update the Repository
Use the `github-agent` MCP to create a new repository under the specified personal account or organization.
- If creating: ensure the repository is initialized.
- If it already exists: verify its status.

### Step 2: Configure Standard Workflows
Add or update the repository's `.github/workflows/container_pipeline.yml` (and any other relevant workflows).
Ensure the Docker build steps use `type=gha,mode=max` caching to prevent 1-hour build timeouts.

Example Docker cache configuration to include:
```yaml
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Step 3: Enable GitHub Pages (via Workflow)
GitHub Pages needs to be configured to build from GitHub Actions.
Run the provided script `scripts/enable_pages.py` to programmatically enable GitHub Pages for the repository.

Usage:
```bash
python scripts/enable_pages.py <owner> <repo_name>
```
*Note: This script uses the `GITHUB_ACCESS_TOKEN` environment variable.*

### Step 4: Verify Provisioning
Ensure all actions have succeeded without exposing secrets in any output or file.
