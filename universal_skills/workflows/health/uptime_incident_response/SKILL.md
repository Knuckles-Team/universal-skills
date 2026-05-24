---
name: uptime_incident_response
description: Parallel execution workflow for uptime incident response using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-uptime-kuma
---

# Parallel Workflow: Uptime Incident Response

This workflow defines the topological parallel execution steps for uptime incident response.

## Steps

### Step 1: detect_down
Execute the detect down phase for the uptime_incident_response workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: detect_down_artifacts
### Step 2: diagnose [depends_on: detect_down]
Execute the diagnose phase for the uptime_incident_response workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: diagnose_artifacts
### Step 3: restart [depends_on: diagnose]
Execute the restart phase for the uptime_incident_response workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: restart_artifacts
### Step 4: verify [depends_on: restart]
Execute the verify phase for the uptime_incident_response workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: verify_artifacts
### Step 5: notify [depends_on: verify]
Execute the notify phase for the uptime_incident_response workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: notify_artifacts
