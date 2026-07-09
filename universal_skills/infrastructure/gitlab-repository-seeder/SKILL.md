---
name: gitlab-repository-seeder
description: >
  GitLab Repository Seeder atomic skill. Creates GitOps project repositories,
  generates scoped Personal Access Tokens, and seeds initial repository file structures using gitlab-mcp.
domain: infrastructure
tags:
  - gitlab
  - gitops
  - projects
  - provisioning
requires:
  - gitlab-mcp
---

# GitLab Repository Seeder Skill

Stateless atomic operation to programmatically provision Git repositories, configure access tokens, and seed compose stack configurations.

## Prerequisites

- `gitlab-mcp` — for GitLab API projects, branches, and token management.

## Steps

### Step 1: Create Projects
Ensure GitOps repositories exist for each platform application (e.g. Twenty CRM, ERPNext, Plane, Caddy, etc.):
- Create empty private projects on the local GitLab CE instance.
- Setup branch defaults (e.g., `main`).

### Step 2: Seed Project Files
Create initial repository configurations:
- Commit the raw `docker-compose.yml` or `swarm-stack.yml` definitions.
- Commit basic readme, configurations, or environmental placeholders.

### Step 3: Generate Personal Access Tokens
Produce scoped access tokens (GitLab PATs) for programmatic pulling/syncing:
- Create project-level or user-level access tokens with `read_repository` or `write_repository` scopes.
- Return the generated token to be securely mapped to GitOps workflows (e.g., Portainer sync).
