---
name: migration_guide_generator
description: Parallel execution workflow for migration guide generator using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-github-mcp
---

# Parallel Workflow: Migration Guide Generator

This workflow defines the topological parallel execution steps for migration guide generator.

## Steps

### Step 1: diff_versions
Execute the diff versions phase for the migration_guide_generator workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: diff_versions_artifacts
### Step 2: identify_breaking_changes [depends_on: diff_versions]
Execute the identify breaking changes phase for the migration_guide_generator workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: identify_breaking_changes_artifacts
### Step 3: generate_guide [depends_on: identify_breaking_changes]
Execute the generate guide phase for the migration_guide_generator workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: generate_guide_artifacts
### Step 4: publish [depends_on: generate_guide]
Execute the publish phase for the migration_guide_generator workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: publish_artifacts
