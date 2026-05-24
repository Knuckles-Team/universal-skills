---
name: uptime_self_healer
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

### Step 2: container-manager-mcp
Locate and inspect the associated container cluster on the target host. Retrieve recent container event log files using `container_manager_mcp` or `portainer-agent` (or SSH run commands via `tunnel-manager`) to diagnose crash loops or startup faults.

### Step 3: container-manager-mcp
Trigger service restoration commands. Restart the target container using `docker_restart_container` via `container-manager-mcp` or redeploy the corresponding stack via `portainer-agent`.

### Step 4: uptime-kuma-agent
Verify recovery by pulling the latest status check heartbeats via `uptime_kuma_status` with `action='get_heartbeats'` to confirm the monitor transitions back to active (online).

### Step 5: user-interaction
Deliver the final uptime status validation report showing the successful self-healing and recovery timeline.
