---
name: reverse_proxy_setup
description: Parallel execution workflow for reverse proxy setup using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-container-manager
---

# Parallel Workflow: Reverse Proxy Setup

This workflow defines the topological parallel execution steps for reverse proxy setup.

## Steps

### Step 1: detect_services
Execute the detect services phase for the reverse_proxy_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: detect_services_artifacts
### Step 2: generate_traefik_config [depends_on: detect_services]
Execute the generate traefik config phase for the reverse_proxy_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: generate_traefik_config_artifacts
### Step 3: deploy [depends_on: generate_traefik_config]
Execute the deploy phase for the reverse_proxy_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: deploy_artifacts
### Step 4: ssl_certs [depends_on: deploy]
Execute the SSL certs phase for the reverse_proxy_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: ssl_certs_artifacts
