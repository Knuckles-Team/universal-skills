---
name: qbittorrent_completed_cleaner
description: >-
  Discovers completed downloads, prompts the user to select torrents to remove, and securely prunes the active dashboard list (optionally deleting files).
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
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
    verifier-agent: [pt_docker, cnt_cm_container_operations]
tags: ['qbittorrent', 'torrents', 'cleaner', 'pruning', 'qbittorrent-agent']
concept: CONCEPT:INFRA-001
---

# Qbittorrent Completed Cleaner Workflow

**CONCEPT:INFRA-001**

Discovers completed downloads, prompts the user to select torrents to remove, and securely prunes the active dashboard list (optionally deleting files).

## Steps

### Step 0: Qbittorrent Agent
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Fetch all completed torrents that are currently seeding or finished downloading using qbittorrent_torrents with the get_torrent_list action.
Expected: `completed_torrent_list`

### Step 1: User Interaction
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Display completed torrents. Prompt the user to select which completed items should be deleted, and confirm if actual data files should also be erased.
Expected: `selected_hashes, delete_files_flag`

### Step 2: Qbittorrent Agent
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Remove the chosen torrents using qbittorrent_torrents with the delete_torrents action, passing the target hashes and deletion options.
Expected: `pruning_results`

### Step 3: KG Persistence [depends_on: qbittorrent-agent]
**Agent**: `verifier-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Qbittorrent Completed Cleaner results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
