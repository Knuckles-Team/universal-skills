---
name: deploy-observability-stack
skill_type: workflow
description: >-
  Deploys Prometheus, Grafana, and Loki in parallel and synthesizes dashboard integrations.
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
tags: [prometheus, grafana, loki, docker, portainer, observability]
concept: CONCEPT:INFRA-001
metadata:
  version: '1.1.0'
---

# Deploy Observability Stack Workflow

**CONCEPT:INFRA-001**

Deploys Prometheus, Grafana, and Loki in parallel and synthesizes dashboard integrations.

## Steps

### Step 1: Prometheus Setup
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Deploy the Prometheus container to scrape system metrics and container stats.
Expected: `prometheus-running`

### Step 2: Grafana Setup [depends_on: none]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Deploy the Grafana container and auto-register Prometheus and Loki data sources.
Expected: `grafana-running`

### Step 3: Loki Setup [depends_on: none]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Deploy the Loki logs aggregation server and configure sidecars.
Expected: `loki-running`

### Step 4: Observability Synth [depends_on: prometheus-setup, grafana-setup, loki-setup]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Configure default system health dashboards, alert rules, and verify final telemetry integration across all services.
Expected: `system-integrated`

### Step 5: KG Persistence [depends_on: Observability Synth]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Observability Stack results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Prometheus Setup; Step 2 — Grafana Setup; Step 3 — Loki Setup
- **After level 0:** Step 4 — Observability Synth
- **After level 1:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
