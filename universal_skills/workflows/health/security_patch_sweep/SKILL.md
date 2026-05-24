---
name: security_patch_sweep
description: Parallel execution workflow for security patch sweep using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-systems-manager
---

# Parallel Workflow: Security Patch Sweep

This workflow defines the topological parallel execution steps for security patch sweep.

## Steps

### Step 1: fan_out_per_host_check_updates
Execute the Fan-out per host: check updates phase for the security_patch_sweep workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_host_check_updates_artifacts
### Step 2: cve_scan [depends_on: fan_out_per_host_check_updates]
Execute the CVE scan phase for the security_patch_sweep workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: cve_scan_artifacts
### Step 3: apply_patches [depends_on: cve_scan]
Execute the apply patches phase for the security_patch_sweep workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: apply_patches_artifacts
### Step 4: reboot_schedule [depends_on: apply_patches]
Execute the reboot schedule phase for the security_patch_sweep workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: reboot_schedule_artifacts
