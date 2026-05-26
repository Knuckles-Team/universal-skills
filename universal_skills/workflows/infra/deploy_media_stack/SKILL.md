---
name: deploy_media_stack
description: >-
  Parallel execution workflow for deploy media stack using the Unified Parallel Engine
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
tags: [infra, deploy-media-stack]
concept: CONCEPT:INFRA-001
---

# Deploy Media Stack Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy media stack using the Unified Parallel Engine

## Steps

### Step 1: Jellyfin
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute jellyfin operations for the Deploy Media Stack workflow.
Expected: `jellyfin_artifacts`

### Step 2: Sonarr
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute sonarr operations for the Deploy Media Stack workflow.
Expected: `sonarr_artifacts`

### Step 3: Radarr
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Execute radarr operations for the Deploy Media Stack workflow.
Expected: `radarr_artifacts`

### Step 4: Prowlarr
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Execute prowlarr operations for the Deploy Media Stack workflow.
Expected: `prowlarr_artifacts`

### Step 5: Bazarr [depends_on: jellyfin, sonarr, radarr, prowlarr]
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute bazarr operations for the Deploy Media Stack workflow.
Expected: `bazarr_artifacts`

### Step 6: KG Persistence [depends_on: bazarr]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Media Stack results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
