---
name: systems-issue-troubleshooter
skill_type: workflow
description: >-
  Inspect logs, find zombie/hung processes, disk space shortages, or corruptions, and remediate using Systems Manager
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: infrastructure deployment and operations
  execution_mode: parallel
  specialist_ids:
    - discovery-agent
    - deployer-agent
    - verifier-agent
    - dns-configurator
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
    verifier-agent: [pt_docker, cnt_cm_container_operations]
    dns-configurator: [adg_rewrites, td_zones]
tags: [infra, systems-issue-troubleshooter]
concept: CONCEPT:INFRA-001
metadata:
  version: '1.6.2'
---

# Systems Issue Troubleshooter Workflow

**CONCEPT:INFRA-001**

Inspect logs, find zombie/hung processes, disk space shortages, or corruptions, and remediate using Systems Manager

## Steps

1. Capture system health with `sm_system_operations` using `action='system_health_check'` and `action='get_os_statistics'`. Verify that both calls return data.
2. Inspect processes with `sm_process_operations` and `action='list_processes'`. Verify that zombie or hung PIDs are listed or confirmed absent.
3. Read disk and logs with `sm_disk_operations` (`action='get_disk_space_report'`) and `sm_file_operations` (`action='get_system_logs'`, `lines=150`). Verify that the disk report and log lines are returned.
4. Present findings and ask the user (skill `user-interaction`) to approve a fix. Verify that the user's explicit choice is recorded before any change.
5. Apply the approved fix with `sm_process_operations` (`action='kill_process'`) or `sm_system_operations` (`action='clean_temp_files'`). Verify that the call reports success.
6. Re-run `sm_system_operations` with `action='system_health_check'`. Verify that the metrics improved compared with step 1.
7. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

### Step 0: collect-system-health [skill: systems-manager]
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Capture general operating system performance stats and health checks using `sm_system_operations` with `action='system_health_check'` and `action='get_os_statistics'`.

### Step 1: inspect-processes [skill: systems-manager]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Retrieve the active process table using `sm_process_operations` with `action='list_processes'` to scan for zombie states, memory leaks, or hung process IDs (PIDs).

### Step 2: inspect-disk-and-logs [skill: systems-manager]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Retrieve disk partition layouts and usage indicators using `sm_disk_operations` with `action='get_disk_space_report'`. Fetch the latest system journal log records using `sm_file_operations` with `action='get_system_logs'` and `lines=150` to detect underlying filesystem or service corruptions.

### Step 3: confirm-remediation [skill: user-interaction]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Present the diagnostic dashboard (including lists of zombie/hung processes, disk bottlenecks, and log error summaries) to the user. Request choice of corrective intervention (e.g. killing a process, running disk cleanups).

### Step 4: apply-approved-remediation [skill: systems-manager]
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute the approved cleanup commands. Terminate rogue process instances using `sm_process_operations` with `action='kill_process'` and target `pid`. Reclaim storage space using `sm_system_operations` with `action='clean_temp_files'` and `action='clean_package_cache'`.

### Step 5: report-remediation [skill: user-interaction]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Present the revised health diagnostic metrics to verify successful remediation and system stabilization.

### Step 6: KG Persistence [depends_on: Step 3, Step 5]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `kill_process` fails | PID is gone or access denied | Re-list with `list_processes` for the current PID and run with a privileged user. |
| Logs call returns nothing | Journal access is restricted | Run `sm_file_operations` as a user in the journal group, or increase `lines`. |
| Disk usage does not drop | Space is held by open files or other partitions | Use `get_disk_space_report` to find the largest consumers and target them. |

## Output
- Systems Issue Troubleshooter results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — collect-system-health; Step 1 — inspect-processes; Step 2 — inspect-disk-and-logs; Step 3 — confirm-remediation; Step 4 — apply-approved-remediation; Step 5 — report-remediation
- **After level 0:** Step 6 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
