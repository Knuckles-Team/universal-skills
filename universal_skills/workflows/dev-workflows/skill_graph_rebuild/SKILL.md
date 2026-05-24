---
name: skill_graph_rebuild
description: Parallel execution workflow for skill graph rebuild using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-graph-os
---

# Parallel Workflow: Skill Graph Rebuild

This workflow defines the topological parallel execution steps for skill graph rebuild.

## Steps

### Step 1: parse_skill_md
Execute the parse SKILL.md phase for the skill_graph_rebuild workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parse_skill_md_artifacts
### Step 2: extract_deps [depends_on: parse_skill_md]
Execute the extract deps phase for the skill_graph_rebuild workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: extract_deps_artifacts
### Step 3: build_graph [depends_on: extract_deps]
Execute the build graph phase for the skill_graph_rebuild workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: build_graph_artifacts
### Step 4: kg_sync [depends_on: build_graph]
Execute the KG sync phase for the skill_graph_rebuild workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: kg_sync_artifacts
