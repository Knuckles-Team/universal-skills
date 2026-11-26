---
name: gitlab-repository-seeder
skill_type: skill
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
metadata:
  version: '1.6.2'
---

# GitLab Repository Seeder Skill

Stateless atomic operation to programmatically provision Git repositories, configure access tokens, and seed compose stack configurations.

## Prerequisites

- `gitlab-mcp` — for GitLab API projects, branches, and token management.

## Steps

1. Create the GitOps projects with the `gitlab-mcp` project tools as empty private projects with a `main` default branch. Verify that the project list from `gitlab-mcp` shows each new project and its `main` branch.
2. Seed the initial files by committing `docker-compose.yml` or `swarm-stack.yml` plus a readme through `gitlab-mcp`. Verify that the repository file listing includes the committed compose file.
3. Generate a scoped access token with `read_repository` or `write_repository` scope through `gitlab-mcp`. Verify that the token record lists the intended scope and that the value is handed only to the GitOps sync consumer.

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

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Project creation returns an error | Name already taken or the caller lacks group permission | List existing projects with `gitlab-mcp` and reuse the existing project or pick an unused path. |
| Commit rejected | Default branch protected or file path invalid | Check the branch protection settings and commit to a new branch or fix the path. |
| Token cannot pull the repository | Token created with the wrong scope or expired | Create a new token with `read_repository` scope and replace the old one in the sync consumer. |
