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

## Injecting an env var / secret into a non-GitOps stack

To push a new environment variable (e.g. a rotated secret) into a deployed
`compose`/standalone stack, use `scripts/portainer_stack_env.py` — it merges the
override into the stack's env list **and** redeploys.

**The drift gotcha (why a plain env-set silently fails):** Portainer stores BOTH
the env list *and its own copy of the stack file*, and that stored copy drifts
from the repo. Two failure modes follow:
1. Setting a value in the env list does nothing unless the stored compose has a
   `- VAR=${VAR}` line to inject it — the container env stays empty.
2. Redeploying with the stored (stale) compose silently reverts repo changes
   (a mount, `PYTHONPATH`, etc. you fixed live).

So **always pass the current repo compose** with `--compose-file`, which pushes
it as the stored content in the same update — keeping the deployed stack and the
repo in lockstep:

```bash
PORTAINER_URL=http://portainer.arpa PORTAINER_TOKEN=… \
python scripts/portainer_stack_env.py --stack-id <id> \
  --set-json /run/overrides.json \
  --compose-file services/<svc>/compose.yml
```

`--set-json` reads `{KEY: VALUE}` from a file so secrets stay off the command
line; `--set KEY=VALUE` is available for non-secret vars. Honors
`PORTAINER_VERIFY` / `--insecure`. Find the stack id via the Portainer stacks
API (or `portainer-mcp`).
