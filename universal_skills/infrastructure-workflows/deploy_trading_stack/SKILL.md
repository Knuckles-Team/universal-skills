---
name: deploy_trading_stack
description: >-
  Parallel execution workflow for deploy trading stack using the Unified Parallel Engine
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
tags: [infra, deploy-trading-stack]
concept: CONCEPT:INFRA-001
---

# Deploy Trading Stack Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy trading stack using the Unified Parallel Engine

## Steps

### Step 1: Data Ingest
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute data ingest operations for the Deploy Trading Stack workflow.
Expected: `data_ingest_artifacts`

### Step 2: Freqtrade [depends_on: data_ingest]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute freqtrade operations for the Deploy Trading Stack workflow.
Expected: `freqtrade_artifacts`

### Step 3: Emerald Exchange [depends_on: freqtrade]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Execute emerald exchange operations for the Deploy Trading Stack workflow.
Expected: `emerald_exchange_artifacts`

### Step 4: Monitoring [depends_on: emerald_exchange]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Execute monitoring operations for the Deploy Trading Stack workflow.
Expected: `monitoring_artifacts`

### Step 5: KG Persistence [depends_on: monitoring]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Trading Stack results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Data Ingest
- **After level 0:** Step 2 — Freqtrade
- **After level 1:** Step 3 — Emerald Exchange
- **After level 2:** Step 4 — Monitoring
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
