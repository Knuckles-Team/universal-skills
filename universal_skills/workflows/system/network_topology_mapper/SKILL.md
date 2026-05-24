---
name: network_topology_mapper
description: Parallel execution workflow for network topology mapper using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-tunnel-manager
---

# Parallel Workflow: Network Topology Mapper

This workflow defines the topological parallel execution steps for network topology mapper.

## Steps

### Step 1: scan_hosts
Execute the scan hosts phase for the network_topology_mapper workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scan_hosts_artifacts
### Step 2: trace_routes [depends_on: scan_hosts]
Execute the trace routes phase for the network_topology_mapper workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: trace_routes_artifacts
### Step 3: build_graph [depends_on: trace_routes]
Execute the build graph phase for the network_topology_mapper workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: build_graph_artifacts
### Step 4: kg_ingest [depends_on: build_graph]
Execute the KG ingest phase for the network_topology_mapper workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: kg_ingest_artifacts
### Step 5: visualize [depends_on: kg_ingest]
Execute the visualize phase for the network_topology_mapper workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: visualize_artifacts
