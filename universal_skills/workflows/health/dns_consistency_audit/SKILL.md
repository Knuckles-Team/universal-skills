---
name: dns_consistency_audit
description: Parallel execution workflow for dns consistency audit using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-adguard-home
---

# Parallel Workflow: Dns Consistency Audit

This workflow defines the topological parallel execution steps for dns consistency audit.

## Steps

### Step 1: list_rewrites
Execute the list rewrites phase for the dns_consistency_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: list_rewrites_artifacts
### Step 2: resolve_each
Execute the resolve each phase for the dns_consistency_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: resolve_each_artifacts
### Step 3: compare
Execute the compare phase for the dns_consistency_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: compare_artifacts
### Step 4: drift_report [depends_on: list_rewrites, resolve_each, compare]
Execute the drift report phase for the dns_consistency_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: drift_report_artifacts
