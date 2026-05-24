---
name: sla_compliance_monitor
description: Parallel execution workflow for sla compliance monitor using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-servicenow
---

# Parallel Workflow: Sla Compliance Monitor

This workflow defines the topological parallel execution steps for sla compliance monitor.

## Steps

### Step 1: check_response_times
Execute the check response times phase for the sla_compliance_monitor workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: check_response_times_artifacts
### Step 2: resolution_times [depends_on: check_response_times]
Execute the resolution times phase for the sla_compliance_monitor workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: resolution_times_artifacts
### Step 3: breach_alerts [depends_on: resolution_times]
Execute the breach alerts phase for the sla_compliance_monitor workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: breach_alerts_artifacts
