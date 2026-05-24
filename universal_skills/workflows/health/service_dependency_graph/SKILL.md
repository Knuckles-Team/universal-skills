---
name: service_dependency_graph
description: Parallel execution workflow for service dependency graph using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-container-manager
---

# Parallel Workflow: Service Dependency Graph

This workflow defines the topological parallel execution steps for service dependency graph.

## Steps

### Step 1: scan_all_containers
Execute the scan all containers phase for the service_dependency_graph workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scan_all_containers_artifacts
### Step 2: extract_env_vars [depends_on: scan_all_containers]
Execute the extract env vars phase for the service_dependency_graph workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: extract_env_vars_artifacts
### Step 3: build_dep_graph [depends_on: extract_env_vars]
Execute the build dep graph phase for the service_dependency_graph workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: build_dep_graph_artifacts
### Step 4: kg_ingest [depends_on: build_dep_graph]
Execute the KG ingest phase for the service_dependency_graph workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: kg_ingest_artifacts
