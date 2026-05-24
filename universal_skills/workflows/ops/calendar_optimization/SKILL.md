---
name: calendar_optimization
description: Parallel execution workflow for calendar optimization using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-nextcloud
---

# Parallel Workflow: Calendar Optimization

This workflow defines the topological parallel execution steps for calendar optimization.

## Steps

### Step 1: scan_events
Execute the scan events phase for the calendar_optimization workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scan_events_artifacts
### Step 2: find_conflicts [depends_on: scan_events]
Execute the find conflicts phase for the calendar_optimization workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: find_conflicts_artifacts
### Step 3: suggest_rearrangements [depends_on: find_conflicts]
Execute the suggest rearrangements phase for the calendar_optimization workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: suggest_rearrangements_artifacts
### Step 4: apply [depends_on: suggest_rearrangements]
Execute the apply phase for the calendar_optimization workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: apply_artifacts
