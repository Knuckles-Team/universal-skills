---
name: systems_issue_troubleshooter
description: Inspect logs, find zombie/hung processes, disk space shortages, or corruptions, and remediate using Systems Manager
tags:
  - infra
  - systems-manager
  - troubleshooting
requires:
  - systems-manager
---

# Systems Issue Troubleshooter Workflow

Inspect operational server environment telemetry, isolate hung or zombie process clusters, analyze journal logs, and execute system cleanup, pruning, and process termination.

## Steps

### Step 0: systems-manager
Capture general operating system performance stats and health checks using `sm_system_operations` with `action='system_health_check'` and `action='get_os_statistics'`.

### Step 1: systems-manager
Retrieve the active process table using `sm_process_operations` with `action='list_processes'` to scan for zombie states, memory leaks, or hung process IDs (PIDs).

### Step 2: systems-manager
Retrieve disk partition layouts and usage indicators using `sm_disk_operations` with `action='get_disk_space_report'`. Fetch the latest system journal log records using `sm_file_operations` with `action='get_system_logs'` and `lines=150` to detect underlying filesystem or service corruptions.

### Step 3: user-interaction
Present the diagnostic dashboard (including lists of zombie/hung processes, disk bottlenecks, and log error summaries) to the user. Request choice of corrective intervention (e.g. killing a process, running disk cleanups).

### Step 4: systems-manager
Execute the approved cleanup commands. Terminate rogue process instances using `sm_process_operations` with `action='kill_process'` and target `pid`. Reclaim storage space using `sm_system_operations` with `action='clean_temp_files'` and `action='clean_package_cache'`.

### Step 5: user-interaction
Present the revised health diagnostic metrics to verify successful remediation and system stabilization.
