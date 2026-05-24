---
name: load_balancer_setup
description: Parallel execution workflow for load balancer setup using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-container-manager
---

# Parallel Workflow: Load Balancer Setup

This workflow defines the topological parallel execution steps for load balancer setup.

## Steps

### Step 1: detect_backends
Execute the detect backends phase for the load_balancer_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: detect_backends_artifacts
### Step 2: configure_haproxy_nginx [depends_on: detect_backends]
Execute the configure haproxy/nginx phase for the load_balancer_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: configure_haproxy_nginx_artifacts
### Step 3: health_checks [depends_on: configure_haproxy_nginx]
Execute the health checks phase for the load_balancer_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: health_checks_artifacts
### Step 4: deploy [depends_on: health_checks]
Execute the deploy phase for the load_balancer_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: deploy_artifacts
