---
name: deploy_backup_system
description: Parallel execution workflow for deploy backup system using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-systems-manager
---

# Parallel Workflow: Deploy Backup System

This workflow defines the topological parallel execution steps for deploy backup system.

## Steps

### Step 1: restic
Execute the restic phase for the deploy_backup_system workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: restic_artifacts
### Step 2: borgmatic
Execute the borgmatic phase for the deploy_backup_system workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: borgmatic_artifacts
### Step 3: rclone
Execute the rclone phase for the deploy_backup_system workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: rclone_artifacts
### Step 4: schedule_cron [depends_on: restic, borgmatic, rclone]
Execute the schedule cron phase for the deploy_backup_system workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: schedule_cron_artifacts
