---
name: infrastructure-monitor
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
  author: agent-utilities
  version: '1.0.0'
  concept: 'CONCEPT:ECO-4.13'
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
Tool: `adguard_home_rewrites(action="list_rewrites")`

### Step 5: kg-persist
Store HealthSnapshot node in KG.
Tool: `graph_write(action="add_node", node_type="HealthSnapshot", ...)`

### Step 6: discover
Proactively identify new metrics or alerts from infrastructure.
Analyze container logs and system metrics for anomalies.
Recommend new monitoring rules to add.
