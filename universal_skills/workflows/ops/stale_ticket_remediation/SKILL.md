---
name: stale_ticket_remediation
description: Parallel execution workflow for stale ticket remediation using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-atlassian
---

# Parallel Workflow: Stale Ticket Remediation

This workflow defines the topological parallel execution steps for stale ticket remediation.

## Steps

### Step 1: find_stale
Execute the find stale phase for the stale_ticket_remediation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: find_stale_artifacts
### Step 2: notify_owners [depends_on: find_stale]
Execute the notify owners phase for the stale_ticket_remediation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: notify_owners_artifacts
### Step 3: escalate [depends_on: notify_owners]
Execute the escalate phase for the stale_ticket_remediation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: escalate_artifacts
### Step 4: auto_close [depends_on: escalate]
Execute the auto-close phase for the stale_ticket_remediation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: auto_close_artifacts
