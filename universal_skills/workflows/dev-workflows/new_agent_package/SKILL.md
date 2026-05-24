---
name: new_agent_package
description: Parallel execution workflow for new agent package using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: New Agent Package

This workflow defines the topological parallel execution steps for new agent package.

## Steps

### Step 1: scaffold
Execute the scaffold phase for the new_agent_package workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scaffold_artifacts
### Step 2: api_client [depends_on: scaffold]
Execute the api-client phase for the new_agent_package workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: api_client_artifacts
### Step 3: mcp_server [depends_on: api_client]
Execute the mcp-server phase for the new_agent_package workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: mcp_server_artifacts
### Step 4: agent [depends_on: mcp_server]
Execute the agent phase for the new_agent_package workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: agent_artifacts
### Step 5: tests [depends_on: agent]
Execute the tests phase for the new_agent_package workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: tests_artifacts
### Step 6: docs [depends_on: tests]
Execute the docs phase for the new_agent_package workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: docs_artifacts
