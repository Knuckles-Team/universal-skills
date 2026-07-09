---
name: infrastructure-monitor
domain: finance-workflows
skill_type: workflow
description: >-
  Continuous infrastructure health monitoring for trading services.
  Discovers new metrics and alerts proactively.
tags: [finance, infrastructure, monitoring, cron]
team_config: trading_department
agent: risk_compliance_officer
cron:
  schedule: "*/15 * * * *"
  enabled: true
  timezone: "America/New_York"
  max_concurrent: 1
metadata:
  version: '1.0.2'
  author: agent-utilities
  concept: 'CONCEPT:ECO-4.7'
---
# Infrastructure Monitor Workflow (Cron: every 15 minutes)

## Workflow Execution Steps

### Step 1: container-health
Check container health for all trading services.
Tool: `portainer_docker(action="docker_list_containers")`

### Step 2: error-traces
Query recent error traces from observability.
Tool: `langfuse_observability(action="trace_list", tags=["finance"])`

### Step 3: system-resources
Check disk/memory/CPU on trading nodes.
Tool: `systems_manager` resource checks.

### Step 4: dns-check
Verify DNS resolution for all trading services.
Tool: `technitium_zones(action="get_records")`

### Step 5: kg-persist
Store HealthSnapshot node in KG.
Tool: `graph_write(action="add_node", node_type="HealthSnapshot", ...)`

### Step 6: discover
Proactively identify new metrics or alerts from infrastructure.
Analyze container logs and system metrics for anomalies.
Recommend new monitoring rules to add.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — container-health; Step 2 — error-traces; Step 3 — system-resources; Step 4 — dns-check; Step 5 — kg-persist; Step 6 — discover

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
