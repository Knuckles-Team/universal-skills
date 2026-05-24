---
name: architecture_diagram_gen
description: Parallel execution workflow for architecture diagram gen using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-github-mcp
---

# Parallel Workflow: Architecture Diagram Gen

This workflow defines the topological parallel execution steps for architecture diagram gen.

## Steps

### Step 1: fan_out_per_component_analyze_code
Execute the Fan-out per component: analyze code phase for the architecture_diagram_gen workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_component_analyze_code_artifacts
### Step 2: c4_diagram [depends_on: fan_out_per_component_analyze_code]
Execute the C4 diagram phase for the architecture_diagram_gen workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: c4_diagram_artifacts
### Step 3: mermaid [depends_on: c4_diagram]
Execute the Mermaid phase for the architecture_diagram_gen workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: mermaid_artifacts
### Step 4: docs [depends_on: mermaid]
Execute the docs phase for the architecture_diagram_gen workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: docs_artifacts
