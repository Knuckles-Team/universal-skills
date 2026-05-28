---
name: caddy-route-manager
description: >
  Caddy Route Manager atomic skill. Manages reverse-proxy configurations,
  ingress routing, and Caddyfile reloads using caddy-mcp or direct Caddyfile manipulation.
domain: infrastructure
tags:
  - caddy
  - reverse-proxy
  - ingress
  - routing
requires:
  - caddy-mcp
  - systems-manager-mcp
---

# Caddy Route Manager Skill

Stateless atomic operation to configure and manage reverse-proxy domain routing entries inside the edge Ingress controller.

## Prerequisites

- `caddy-mcp` — for communicating with Caddy admin API or reloading configuration.
- `systems-manager-mcp` — for direct reading and editing of the global `/home/apps/caddy/Caddyfile` configuration.

## Steps

### Step 1: Parse and Locate Target Caddyfile
Verify the location of the active Caddy configuration:
- Locate the primary Caddyfile at `/home/apps/caddy/Caddyfile`.
- Inspect the file structure and verify that it parses cleanly.

### Step 2: Ingress Block Modification
Create or update domain routing blocks for the target service:
- Formulate a compliant routing block targeting the service's subdomain and internal overlay port:
  ```caddy
  <service-name>.arpa {
      reverse_proxy <container-name>:<internal-port>
  }
  ```
- Insert or append the block inside the Caddyfile safely.
- Ensure appropriate TLS configurations are declared (e.g. self-signed internal TLS CA or local certificates).

### Step 3: Config Verification & Reload
Apply configurations dynamically with zero downtime:
- Run validation checks on Caddy syntax: `caddy validate --config /home/apps/caddy/Caddyfile`.
- Trigger hot reload via `caddy-mcp` administrative tools or by signaling the Caddy process (`caddy reload`).
- Verify routing health by sending check requests.
