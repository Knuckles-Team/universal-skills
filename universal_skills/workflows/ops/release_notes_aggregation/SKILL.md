---
name: release_notes_aggregation
description: Parallel execution workflow for release notes aggregation using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-atlassian
---

# Parallel Workflow: Release Notes Aggregation

This workflow defines the topological parallel execution steps for release notes aggregation.

## Steps

### Step 1: jira_tickets
Execute the Jira tickets phase for the release_notes_aggregation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: jira_tickets_artifacts
### Step 2: prs
Execute the PRs phase for the release_notes_aggregation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: prs_artifacts
### Step 3: commits
Execute the commits phase for the release_notes_aggregation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: commits_artifacts
### Step 4: aggregate [depends_on: jira_tickets, prs, commits]
Execute the aggregate phase for the release_notes_aggregation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: aggregate_artifacts
### Step 5: publish [depends_on: aggregate]
Execute the publish phase for the release_notes_aggregation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: publish_artifacts
