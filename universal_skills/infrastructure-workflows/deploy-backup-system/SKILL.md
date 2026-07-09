---
name: deploy-backup-system
description: >-
  Parallel execution workflow for deploy backup system using the Unified Parallel Engine
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
tags: [infra, deploy-backup-system]
concept: CONCEPT:INFRA-001
---

# Deploy Backup System Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy backup system using the Unified Parallel Engine

## Steps

### Step 1: Restic
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute restic operations for the Deploy Backup System workflow.
Expected: `restic_artifacts`

### Step 2: Borgmatic
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute borgmatic operations for the Deploy Backup System workflow.
Expected: `borgmatic_artifacts`

### Step 3: Rclone
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Execute rclone operations for the Deploy Backup System workflow.
Expected: `rclone_artifacts`

### Step 4: Schedule Cron [depends_on: restic, borgmatic, rclone]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Execute schedule cron operations for the Deploy Backup System workflow.
Expected: `schedule_cron_artifacts`

### Step 5: KG Persistence [depends_on: schedule_cron]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Backup System results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Restic; Step 2 — Borgmatic; Step 3 — Rclone
- **After level 0:** Step 4 — Schedule Cron
- **After level 1:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
