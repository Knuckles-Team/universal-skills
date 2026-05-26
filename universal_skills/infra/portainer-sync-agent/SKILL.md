---
name: portainer-sync-agent
description: >
  Portainer Sync Agent atomic skill. Connects to Portainer API, resolves environment IDs,
  creates or redeploys stacks, and wires GitOps auto-sync configurations using portainer-mcp.
domain: infrastructure
tags:
  - portainer
  - GitOps
  - stacks
  - sync
requires:
  - portainer-mcp
---

# Portainer Sync Agent Skill

Stateless atomic operation to deploy platform applications to target environments using GitOps deployment pipelines.

## Prerequisites

- `portainer-mcp` — for executing stack query, creation, updates, and environment queries.

## Steps

### Step 1: Query Portainer Environments
List all active endpoints and environments managed by Portainer, mapping target Swarm manager cluster or standalone node IDs.

### Step 2: Configure GitOps / Pull Stacks
Create or redeploy application stacks in Portainer pointing directly to the Git repository source:
- Set repository URL (e.g. `http://gitlab.arpa/gitops/my-service.git`).
- Set target branch (e.g., `main`).
- Input generated credentials (GitLab username and PAT).
- Enable auto-update (webhook or periodic polling) to ensure runtime matches repository state.

### Step 3: Deploy Stack Lifecycle
Deploy the stack:
- Trigger immediate creation or deployment.
- Verify status changes to `Active` or `Healthy`.
