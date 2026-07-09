---
name: deploy-full-homelab
skill_type: workflow
description: >-
  Parallel execution workflow for deploy full homelab using the Unified Parallel Engine
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
tags: [infra, deploy-full-homelab]
concept: CONCEPT:INFRA-001
metadata:
  version: '1.2.0'
---

# Deploy Full Homelab Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy full homelab using the Unified Parallel Engine

## Steps

### Step 1: Prereqs
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute prereqs operations for the Deploy Full Homelab workflow.
Expected: `prereqs_artifacts`

### Step 2: Core Infra [depends_on: prereqs]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute core infra operations for the Deploy Full Homelab workflow.
Expected: `core_infra_artifacts`

### Step 3: Services [depends_on: core_infra]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Execute services operations for the Deploy Full Homelab workflow.
Expected: `services_artifacts`

### Step 4: Observability [depends_on: services]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Execute observability operations for the Deploy Full Homelab workflow.
Expected: `observability_artifacts`

### Step 5: Dns [depends_on: observability]
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute dns operations for the Deploy Full Homelab workflow.
Expected: `dns_artifacts`

### Step 6: KG Persistence [depends_on: dns]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Full Homelab results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Prereqs
- **After level 0:** Step 2 — Core Infra
- **After level 1:** Step 3 — Services
- **After level 2:** Step 4 — Observability
- **After level 3:** Step 5 — Dns
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
