---
name: cloudflare_tunnel_setup
description: Parallel execution workflow for cloudflare tunnel setup using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-tunnel-manager
---

# Parallel Workflow: Cloudflare Tunnel Setup

This workflow defines the topological parallel execution steps for cloudflare tunnel setup.

## Steps

### Step 1: create_tunnel
Execute the create tunnel phase for the cloudflare_tunnel_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: create_tunnel_artifacts
### Step 2: configure_dns [depends_on: create_tunnel]
Execute the configure DNS phase for the cloudflare_tunnel_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: configure_dns_artifacts
### Step 3: verify_routing [depends_on: configure_dns]
Execute the verify routing phase for the cloudflare_tunnel_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: verify_routing_artifacts
### Step 4: monitor [depends_on: verify_routing]
Execute the monitor phase for the cloudflare_tunnel_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: monitor_artifacts
