---
name: systems_issue_troubleshooter
description: >-
  Inspect logs, find zombie/hung processes, disk space shortages, or corruptions, and remediate using Systems Manager
domain: infra
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
---

# Systems Issue Troubleshooter Workflow

**CONCEPT:INFRA-001**

Inspect logs, find zombie/hung processes, disk space shortages, or corruptions, and remediate using Systems Manager

## Steps

### Step 0: Systems Manager
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Capture general operating system performance stats and health checks using `sm_system_operations` with `action='system_health_check'` and `action='get_os_statistics'`.

### Step 1: Systems Manager
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Retrieve the active process table using `sm_process_operations` with `action='list_processes'` to scan for zombie states, memory leaks, or hung process IDs (PIDs).

### Step 2: Systems Manager
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Retrieve disk partition layouts and usage indicators using `sm_disk_operations` with `action='get_disk_space_report'`. Fetch the latest system journal log records using `sm_file_operations` with `action='get_system_logs'` and `lines=150` to detect underlying filesystem or service corruptions.

### Step 3: User Interaction
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Present the diagnostic dashboard (including lists of zombie/hung processes, disk bottlenecks, and log error summaries) to the user. Request choice of corrective intervention (e.g. killing a process, running disk cleanups).

### Step 4: Systems Manager
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute the approved cleanup commands. Terminate rogue process instances using `sm_process_operations` with `action='kill_process'` and target `pid`. Reclaim storage space using `sm_system_operations` with `action='clean_temp_files'` and `action='clean_package_cache'`.

### Step 5: User Interaction
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Present the revised health diagnostic metrics to verify successful remediation and system stabilization.

### Step 6: KG Persistence [depends_on: user-interaction]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Systems Issue Troubleshooter results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Systems Manager; Step 1 — Systems Manager; Step 2 — Systems Manager; Step 3 — User Interaction; Step 4 — Systems Manager; Step 5 — User Interaction
- **After level 0:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
