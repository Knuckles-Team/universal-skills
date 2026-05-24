---
name: disk_space_remediation
description: Parallel execution workflow for disk space remediation using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-systems-manager
---

# Parallel Workflow: Disk Space Remediation

This workflow defines the topological parallel execution steps for disk space remediation.

## Steps

### Step 1: sequential_scan
Execute the Sequential: scan phase for the disk_space_remediation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: sequential_scan_artifacts
### Step 2: identify_bloat [depends_on: sequential_scan]
Execute the identify bloat phase for the disk_space_remediation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: identify_bloat_artifacts
### Step 3: prune [depends_on: identify_bloat]
Execute the prune phase for the disk_space_remediation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: prune_artifacts
### Step 4: verify [depends_on: prune]
Execute the verify phase for the disk_space_remediation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: verify_artifacts
