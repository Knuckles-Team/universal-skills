---
name: qbittorrent-completed-cleaner
skill_type: workflow
description: >-
  Discovers completed downloads, prompts the user to select torrents to remove, and securely prunes the active dashboard list (optionally deleting files).
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
tags: ['qbittorrent', 'torrents', 'cleaner', 'pruning', 'qbittorrent-agent']
concept: CONCEPT:INFRA-001
metadata:
  version: '1.2.1'
---

# Qbittorrent Completed Cleaner Workflow

**CONCEPT:INFRA-001**

Discovers completed downloads, prompts the user to select torrents to remove, and securely prunes the active dashboard list (optionally deleting files).

## Steps

### Step 0: list-completed-torrents [skill: qbittorrent-agent]
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Fetch all completed torrents that are currently seeding or finished downloading using qbittorrent_torrents with the get_torrent_list action.
Expected: `completed_torrent_list`

### Step 1: User Interaction
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Display completed torrents. Prompt the user to select which completed items should be deleted, and confirm if actual data files should also be erased.
Expected: `selected_hashes, delete_files_flag`

### Step 2: delete-selected-torrents [skill: qbittorrent-agent]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Remove the chosen torrents using qbittorrent_torrents with the delete_torrents action, passing the target hashes and deletion options.
Expected: `pruning_results`

### Step 3: KG Persistence [depends_on: Step 0, Step 2]
**Agent**: `verifier-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Qbittorrent Completed Cleaner results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — list-completed-torrents; Step 1 — User Interaction; Step 2 — delete-selected-torrents
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
