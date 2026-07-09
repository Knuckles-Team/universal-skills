---
name: deploy-message-queue
skill_type: workflow
description: >-
  Parallel execution workflow for deploy message queue using the Unified Parallel Engine
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
tags: [infra, deploy-message-queue]
concept: CONCEPT:INFRA-001
metadata:
  version: '1.0.2'
---

# Deploy Message Queue Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy message queue using the Unified Parallel Engine

## Steps

### Step 1: Rabbitmq Nats
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute rabbitmq nats operations for the Deploy Message Queue workflow.
Expected: `rabbitmq_nats_artifacts`

### Step 2: Consumers [depends_on: rabbitmq_nats]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute consumers operations for the Deploy Message Queue workflow.
Expected: `consumers_artifacts`

### Step 3: Dead Letter [depends_on: consumers]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Execute dead letter operations for the Deploy Message Queue workflow.
Expected: `dead_letter_artifacts`

### Step 4: Monitor [depends_on: dead_letter]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Execute monitor operations for the Deploy Message Queue workflow.
Expected: `monitor_artifacts`

### Step 5: KG Persistence [depends_on: monitor]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Message Queue results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Rabbitmq Nats
- **After level 0:** Step 2 — Consumers
- **After level 1:** Step 3 — Dead Letter
- **After level 2:** Step 4 — Monitor
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
