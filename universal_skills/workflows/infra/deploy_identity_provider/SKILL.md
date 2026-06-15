---
name: deploy_identity_provider
description: >-
  Parallel execution workflow for deploy identity provider using the Unified Parallel Engine
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
tags: [infra, deploy-identity-provider]
concept: CONCEPT:INFRA-001
---

# Deploy Identity Provider Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy identity provider using the Unified Parallel Engine

## Steps

### Step 1: Keycloak Authelia
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute keycloak authelia operations for the Deploy Identity Provider workflow.
Expected: `keycloak_authelia_artifacts`

### Step 2: Oidc Config [depends_on: keycloak_authelia]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute oidc config operations for the Deploy Identity Provider workflow.
Expected: `oidc_config_artifacts`

### Step 3: App Integration [depends_on: oidc_config]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Execute app integration operations for the Deploy Identity Provider workflow.
Expected: `app_integration_artifacts`

### Step 4: KG Persistence [depends_on: app_integration]
**Agent**: `verifier-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Identity Provider results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Keycloak Authelia
- **After level 0:** Step 2 — Oidc Config
- **After level 1:** Step 3 — App Integration
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
