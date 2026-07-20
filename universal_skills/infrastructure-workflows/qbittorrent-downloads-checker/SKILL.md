---
name: qbittorrent-downloads-checker
skill_type: workflow
description: >-
  Connects to your qBittorrent server, lists active and completed torrents, and displays a comprehensive download progress dashboard.
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
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
    verifier-agent: [pt_docker, cnt_cm_container_operations]
tags: ['qbittorrent', 'torrents', 'downloads', 'media', 'qbittorrent-agent']
concept: CONCEPT:INFRA-001
metadata:
  version: '1.2.1'
---

# Qbittorrent Downloads Checker Workflow

**CONCEPT:INFRA-001**

Connects to your qBittorrent server, lists active and completed torrents, and displays a comprehensive download progress dashboard.

## Steps

### Step 0: Qbittorrent Agent
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Fetch all active and completed torrents, state information, and progress rates using qbittorrent_torrents with the get_torrent_list action.
Expected: `active_torrent_list`

### Step 1: Systems Manager
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Query the available host disk capacity metrics to verify storage headroom for active downloads.
Expected: `disk_space_metrics`

### Step 2: User Interaction
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Present a comprehensive downloading status and disk capacity report, highlighting completed items and active disk headroom warnings.
Expected: `view_confirmation`

### Step 3: KG Persistence [depends_on: user-interaction]
**Agent**: `verifier-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Qbittorrent Downloads Checker results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Qbittorrent Agent; Step 1 — Systems Manager; Step 2 — User Interaction
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
