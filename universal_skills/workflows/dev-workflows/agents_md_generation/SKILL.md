---
name: agents_md_generation
description: Parallel execution workflow for agents md generation using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Agents Md Generation

This workflow defines the topological parallel execution steps for agents md generation.

## Steps

### Step 1: analyze
Execute the analyze phase for the agents_md_generation workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: analyze_artifacts
### Step 2: generate_agents_md [depends_on: analyze]
Execute the generate AGENTS.md phase for the agents_md_generation workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: generate_agents_md_artifacts
### Step 3: pr [depends_on: generate_agents_md]
Execute the PR phase for the agents_md_generation workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pr_artifacts
