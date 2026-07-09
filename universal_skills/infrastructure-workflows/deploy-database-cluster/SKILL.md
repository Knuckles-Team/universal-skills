---
name: deploy-database-cluster
description: >-
  Parallel execution workflow for deploy database cluster using the Unified Parallel Engine
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
tags: [infra, deploy-database-cluster]
concept: CONCEPT:INFRA-001
---

# Deploy Database Cluster Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy database cluster using the Unified Parallel Engine

## Steps

### Step 1: Postgres Primary
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute postgres primary operations for the Deploy Database Cluster workflow.
Expected: `postgres_primary_artifacts`

### Step 2: Replicas [depends_on: postgres_primary]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute replicas operations for the Deploy Database Cluster workflow.
Expected: `replicas_artifacts`

### Step 3: Pgbouncer [depends_on: replicas]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Execute pgbouncer operations for the Deploy Database Cluster workflow.
Expected: `pgbouncer_artifacts`

### Step 4: Monitoring [depends_on: pgbouncer]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Execute monitoring operations for the Deploy Database Cluster workflow.
Expected: `monitoring_artifacts`

### Step 5: KG Persistence [depends_on: monitoring]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Database Cluster results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Postgres Primary
- **After level 0:** Step 2 — Replicas
- **After level 1:** Step 3 — Pgbouncer
- **After level 2:** Step 4 — Monitoring
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
