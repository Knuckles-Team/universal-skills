---
name: deploy_mcp_servers
description: Parallel execution workflow for deploy mcp servers using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-portainer
---

# Parallel Workflow: Deploy Mcp Servers

This workflow defines the topological parallel execution steps for deploy mcp servers.

## Steps

### Step 1: all_37_mcp_server_containers__waves
Execute the all 37 MCP server containers  waves phase for the deploy_mcp_servers workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: all_37_mcp_server_containers__waves_artifacts
