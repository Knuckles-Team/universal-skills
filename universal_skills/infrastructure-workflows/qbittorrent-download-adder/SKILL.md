---
name: qbittorrent-download-adder
skill_type: workflow
description: >-
  Prompts the user for a torrent/magnet download link and custom save parameters, then schedules and starts the download on qBittorrent.
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: infrastructure deployment and operations
  execution_mode: parallel
  specialist_ids:
    - discovery-agent
    - deployer-agent
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
tags: ['qbittorrent', 'torrents', 'adder', 'downloads', 'qbittorrent-agent']
concept: CONCEPT:INFRA-001
metadata:
  version: '1.2.1'
---

# Qbittorrent Download Adder Workflow

**CONCEPT:INFRA-001**

Prompts the user for a torrent/magnet download link and custom save parameters, then schedules and starts the download on qBittorrent.

## Steps

### Step 0: User Interaction
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Prompt the user for the magnet link, torrent URL, custom save path category, and queue priorities.
Expected: `download_link, save_category, start_immediately`

### Step 1: Qbittorrent Agent
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Schedule the new download by calling qbittorrent_torrents with the add_new_torrent action, passing the target link and parameters.
Expected: `addition_result`

### Step 2: KG Persistence [depends_on: qbittorrent-agent]
**Agent**: `deployer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Qbittorrent Download Adder results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — User Interaction; Step 1 — Qbittorrent Agent
- **After level 0:** Step 2 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
