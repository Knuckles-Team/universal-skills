---
name: incident_postmortem_pipeline
description: Parallel execution workflow for incident postmortem pipeline using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-github-mcp
---

# Parallel Workflow: Incident Postmortem Pipeline

This workflow defines the topological parallel execution steps for incident postmortem pipeline.

## Steps

### Step 1: gather_logs
Execute the gather logs phase for the incident_postmortem_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: gather_logs_artifacts
### Step 2: timeline [depends_on: gather_logs]
Execute the timeline phase for the incident_postmortem_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: timeline_artifacts
### Step 3: root_cause [depends_on: timeline]
Execute the root cause phase for the incident_postmortem_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: root_cause_artifacts
### Step 4: action_items [depends_on: root_cause]
Execute the action items phase for the incident_postmortem_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: action_items_artifacts
### Step 5: doc [depends_on: action_items]
Execute the doc phase for the incident_postmortem_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: doc_artifacts
### Step 6: pr [depends_on: doc]
Execute the PR phase for the incident_postmortem_pipeline workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pr_artifacts
