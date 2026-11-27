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
  minute: "0,15,30,45"
  enabled: true
  timezone: "America/New_York"
  max_concurrent: 1
metadata:
  version: '1.7.0'
  author: Knuckles-Team
  concept: 'CONCEPT:ECO-4.7'
---
# Infrastructure Monitor Workflow (Cron: every 15 minutes)

## Workflow Execution Steps

### Step 1: container-health
Check container health for all trading services.
Tool: `portainer_list_containers()`

### Step 2: error-traces
Query recent error traces from observability.
Tool: `langfuse_trace_list(tags=["finance"])`

### Step 3: system-resources
Check disk/memory/CPU on trading nodes.
Tool: `systems_manager` resource checks.

### Step 4: dns-check
Verify DNS resolution for all trading services.
Tool: `technitium_dns_get_records()`

### Step 5: kg-persist
Store HealthSnapshot node in KG.
Tool: `graph_write(action="add_node", node_type="HealthSnapshot", ...)`

### Step 6: discover
Proactively identify new metrics or alerts from infrastructure.
Analyze container logs and system metrics for anomalies.
Recommend new monitoring rules to add.

## Steps

1. List the trading containers with `portainer_list_containers()`.
   Verify that every trading service appears and none is unhealthy or restarting.
2. Pull recent error traces with `langfuse_trace_list(tags=["finance"])`.
   Verify that the result is returned and any error traces are noted for the snapshot.
3. Check disk, memory and CPU on the trading nodes with the `systems_manager` resource checks.
   Verify that each node returned a reading for all three resources.
4. Check DNS with `technitium_dns_get_records()`.
   Verify that every trading service name resolves to a record.
5. Persist the results with `graph_write(action="add_node", node_type="HealthSnapshot", ...)`.
   Verify that the call returns a node id for the new HealthSnapshot.
6. Scan container logs for anomalies with `docker logs --tail 200 <container> 2>&1 | grep -iE "error|warn|timeout"` and recommend new monitoring rules.
   Verify that the output lists each recommended rule, or states that none were found.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `portainer_list_containers()` errors or times out | Portainer MCP server unreachable or credentials expired | Confirm the portainer MCP server is reachable, then record the check as failed in the HealthSnapshot and alert instead of skipping it |
| `langfuse_trace_list` returns nothing for every run | The `finance` tag is missing from traces or Langfuse is down | Query without the tag filter to confirm Langfuse answers, and flag the missing tag as a finding |
| `graph_write` is rejected | arbora is unreachable or the node type is not in the ontology | Run the steps natively without delegation and store the snapshot once `graph_write` succeeds; report the rejection text |
| A cron run overlaps the previous one | `max_concurrent: 1` is set but a run exceeded 15 minutes | Check the previous run's slow step and raise its timeout or reduce the scope of that check |

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — container-health; Step 2 — error-traces; Step 3 — system-resources; Step 4 — dns-check; Step 5 — kg-persist; Step 6 — discover

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
