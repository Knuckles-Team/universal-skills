---
name: backup_verification
description: Parallel execution workflow for backup verification using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-systems-manager
---

# Parallel Workflow: Backup Verification

This workflow defines the topological parallel execution steps for backup verification.

## Steps

### Step 1: fan_out_per_backup_target_restore_test
Execute the Fan-out per backup target: restore test phase for the backup_verification workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_backup_target_restore_test_artifacts
### Step 2: integrity_check [depends_on: fan_out_per_backup_target_restore_test]
Execute the integrity check phase for the backup_verification workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: integrity_check_artifacts
### Step 3: report [depends_on: integrity_check]
Execute the report phase for the backup_verification workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
