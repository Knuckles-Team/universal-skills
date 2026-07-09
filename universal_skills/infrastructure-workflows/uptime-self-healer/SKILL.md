---
name: uptime-self-healer
description: Detect down services in Uptime Kuma and automatically restore them using Container Manager or Portainer
tags:
  - infra
  - self-healing
  - uptime-kuma
requires:
  - uptime-kuma-agent
  - container-manager-mcp
  - portainer-agent
  - tunnel-manager
---

# Uptime Kuma Self-Healer Workflow

Query Uptime Kuma monitor lists for inactive/down status metrics, auto-resolve targeting strategies, and invoke container, stack, or host interventions to heal services.

## Steps

### Step 0: uptime-kuma-agent
Retrieve current states for all configured system monitors using `uptime_kuma_monitors` with `action='get_monitors'`.

### Step 1: user-interaction
Scan the response payloads to isolate monitors returning down/offline statuses (e.g., status 0). Request confirmation from the user to launch a targeted self-healing execution.
Depends On: Step 0

### Step 2: container-manager-mcp
Locate and inspect the associated container cluster on the target host. Retrieve recent container event log files using `container_manager_mcp` to diagnose crash loops or startup faults.
Depends On: Step 1

### Step 3: portainer-agent
Query the Portainer environment and stack details associated with the down monitor to assess stack-level configurations.
Depends On: Step 1

### Step 4: container-manager-mcp
Trigger service restoration commands. Restart the target container using `docker_restart_container` via `container-manager-mcp` or redeploy the corresponding stack via `portainer-agent`.
Depends On: Step 2, Step 3

### Step 5: uptime-kuma-agent
Verify recovery by pulling the latest status check heartbeats via `uptime_kuma_status` with `action='get_heartbeats'` to confirm the monitor transitions back to active (online).
Depends On: Step 4

### Step 6: user-interaction
Deliver the final uptime status validation report showing the successful self-healing and recovery timeline.
Depends On: Step 5

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — uptime-kuma-agent; Step 1 — user-interaction; Step 2 — container-manager-mcp; Step 3 — portainer-agent; Step 4 — container-manager-mcp; Step 5 — uptime-kuma-agent; Step 6 — user-interaction

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
