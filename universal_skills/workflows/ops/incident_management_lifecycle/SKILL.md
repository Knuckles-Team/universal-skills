---
name: incident_management_lifecycle
description: Parallel execution workflow for incident management lifecycle using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-servicenow
---

# Parallel Workflow: Incident Management Lifecycle

This workflow defines the topological parallel execution steps for incident management lifecycle.

## Steps

### Step 1: detect
Execute the detect phase for the incident_management_lifecycle workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: detect_artifacts
### Step 2: classify [depends_on: detect]
Execute the classify phase for the incident_management_lifecycle workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: classify_artifacts
### Step 3: assign [depends_on: classify]
Execute the assign phase for the incident_management_lifecycle workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: assign_artifacts
### Step 4: investigate [depends_on: assign]
Execute the investigate phase for the incident_management_lifecycle workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: investigate_artifacts
### Step 5: resolve [depends_on: investigate]
Execute the resolve phase for the incident_management_lifecycle workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: resolve_artifacts
### Step 6: postmortem [depends_on: resolve]
Execute the postmortem phase for the incident_management_lifecycle workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: postmortem_artifacts
