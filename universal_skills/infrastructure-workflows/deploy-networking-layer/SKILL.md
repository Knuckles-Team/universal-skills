---
name: deploy-networking-layer
skill_type: workflow
description: >-
  Parallel execution workflow for deploy networking layer using the Unified Parallel Engine
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
tags: [infra, deploy-networking-layer]
concept: CONCEPT:INFRA-001
metadata:
  version: '1.0.2'
---

# Deploy Networking Layer Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy networking layer using the Unified Parallel Engine

## Steps

### Step 1: Wireguard
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute wireguard operations for the Deploy Networking Layer workflow.
Expected: `wireguard_artifacts`

### Step 2: Caddy [depends_on: wireguard]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute caddy operations for the Deploy Networking Layer workflow.
Expected: `caddy_artifacts`

### Step 3: Technitium [depends_on: caddy]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Execute technitium operations for the Deploy Networking Layer workflow.
Expected: `technitium_artifacts`

### Step 4: Cloudflare Tunnel [depends_on: technitium]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Execute cloudflare tunnel operations for the Deploy Networking Layer workflow.
Expected: `cloudflare_tunnel_artifacts`

### Step 5: KG Persistence [depends_on: cloudflare_tunnel]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Networking Layer results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Wireguard
- **After level 0:** Step 2 — Caddy
- **After level 1:** Step 3 — Technitium
- **After level 2:** Step 4 — Cloudflare Tunnel
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
