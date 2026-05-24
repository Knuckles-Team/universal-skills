---
name: tunnel_health_monitor
description: Parallel execution workflow for tunnel health monitor using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-tunnel-manager
---

# Parallel Workflow: Tunnel Health Monitor

This workflow defines the topological parallel execution steps for tunnel health monitor.

## Steps

### Step 1: fan_out_per_tunnel_test_connectivity
Execute the Fan-out per tunnel: test connectivity phase for the tunnel_health_monitor workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_tunnel_test_connectivity_artifacts
### Step 2: latency [depends_on: fan_out_per_tunnel_test_connectivity]
Execute the latency phase for the tunnel_health_monitor workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: latency_artifacts
### Step 3: bandwidth [depends_on: latency]
Execute the bandwidth phase for the tunnel_health_monitor workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: bandwidth_artifacts
### Step 4: report [depends_on: bandwidth]
Execute the report phase for the tunnel_health_monitor workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
