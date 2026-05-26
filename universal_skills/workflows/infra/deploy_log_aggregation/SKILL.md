---
name: deploy_log_aggregation
description: >-
  Parallel execution workflow for deploy log aggregation using the Unified Parallel Engine
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
tags: [infra, deploy-log-aggregation]
concept: CONCEPT:INFRA-001
---

# Deploy Log Aggregation Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy log aggregation using the Unified Parallel Engine

## Steps

### Step 1: Vector
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute vector operations for the Deploy Log Aggregation workflow.
Expected: `vector_artifacts`

### Step 2: Loki
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute loki operations for the Deploy Log Aggregation workflow.
Expected: `loki_artifacts`

### Step 3: Grafana
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Execute grafana operations for the Deploy Log Aggregation workflow.
Expected: `grafana_artifacts`

### Step 4: Alerting Rules [depends_on: vector, loki, grafana]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Execute alerting rules operations for the Deploy Log Aggregation workflow.
Expected: `alerting_rules_artifacts`

### Step 5: KG Persistence [depends_on: alerting_rules]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Log Aggregation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
