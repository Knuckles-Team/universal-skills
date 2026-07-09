---
name: deploy-productivity-stack
skill_type: workflow
description: >-
  Parallel execution workflow for deploy productivity stack using the Unified Parallel Engine
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
tags: [infra, deploy-productivity-stack]
concept: CONCEPT:INFRA-001
metadata:
  version: '1.1.0'
---

# Deploy Productivity Stack Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy productivity stack using the Unified Parallel Engine

## Steps

### Step 1: Nextcloud
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute nextcloud operations for the Deploy Productivity Stack workflow.
Expected: `nextcloud_artifacts`

### Step 2: Mealie
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute mealie operations for the Deploy Productivity Stack workflow.
Expected: `mealie_artifacts`

### Step 3: Listmonk
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Execute listmonk operations for the Deploy Productivity Stack workflow.
Expected: `listmonk_artifacts`

### Step 4: Dns Rewrites [depends_on: nextcloud, mealie, listmonk]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Execute dns rewrites operations for the Deploy Productivity Stack workflow.
Expected: `dns_rewrites_artifacts`

### Step 5: KG Persistence [depends_on: dns_rewrites]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Productivity Stack results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Nextcloud; Step 2 — Mealie; Step 3 — Listmonk
- **After level 0:** Step 4 — Dns Rewrites
- **After level 1:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
