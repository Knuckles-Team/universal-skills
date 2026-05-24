---
name: architecture_review_swarm
description: Parallel execution workflow for architecture review swarm using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-github-mcp
---

# Parallel Workflow: Architecture Review Swarm

This workflow defines the topological parallel execution steps for architecture review swarm.

## Steps

### Step 1: c4_diagram
Execute the C4 diagram phase for the architecture_review_swarm workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: c4_diagram_artifacts
### Step 2: dependency_graph
Execute the dependency graph phase for the architecture_review_swarm workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: dependency_graph_artifacts
### Step 3: coupling_analysis
Execute the coupling analysis phase for the architecture_review_swarm workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: coupling_analysis_artifacts
### Step 4: security
Execute the security phase for the architecture_review_swarm workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: security_artifacts
### Step 5: report [depends_on: c4_diagram, dependency_graph, coupling_analysis, security]
Execute the report phase for the architecture_review_swarm workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
