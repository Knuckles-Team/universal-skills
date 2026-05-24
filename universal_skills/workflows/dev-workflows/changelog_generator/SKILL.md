---
name: changelog_generator
description: Parallel execution workflow for changelog generator using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Changelog Generator

This workflow defines the topological parallel execution steps for changelog generator.

## Steps

### Step 1: parse_commits
Execute the parse commits phase for the changelog_generator workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parse_commits_artifacts
### Step 2: classify [depends_on: parse_commits]
Execute the classify phase for the changelog_generator workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: classify_artifacts
### Step 3: generate_notes [depends_on: classify]
Execute the generate notes phase for the changelog_generator workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: generate_notes_artifacts
### Step 4: publish [depends_on: generate_notes]
Execute the publish phase for the changelog_generator workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: publish_artifacts
