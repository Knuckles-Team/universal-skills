---
name: smart-home-automation-orchestrator
skill_type: workflow
description: >-
  Interacts with Home Assistant using home-assistant-agent to read device states, query calendar schedules, and trigger specific smart home services, scenes, scripts, or events.
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: infrastructure deployment and operations
  execution_mode: parallel
  specialist_ids:
    - discovery-agent
    - deployer-agent
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
tags: ['home-assistant', 'iot', 'automation', 'scene-management', 'home-assistant-agent']
concept: CONCEPT:INFRA-001
metadata:
  version: '1.7.0'
---

# Smart Home Automation Orchestrator Workflow

**CONCEPT:INFRA-001**

Interacts with Home Assistant using home-assistant-agent to read device states, query calendar schedules, and trigger specific smart home services, scenes, scripts, or events.

## Steps

1. Read device states and calendar events with `home_assistant_states` (`list_states`) and `home_assistant_calendar` (`get_calendar_events`). Verify that `sensor_states` and `calendar_schedules` are non-empty.
2. Trigger the scene or service with `home_assistant_services` (`call_service`). Verify that `service_call_logs` shows a success response for each call.
3. Re-read the affected entity with `home_assistant_states` (`list_states`). Verify that its state matches the intended scene.
4. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

### Step 0: collect-home-state [skill: home-assistant-agent]
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Retrieve current device states, entity metrics, and active calendar event triggers using home_assistant_states list_states and home_assistant_calendar get_calendar_events tools. Target sensor context: {{task}}
Expected: `sensor_states, calendar_schedules, target_devices`

### Step 1: execute-home-automation [skill: home-assistant-agent]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute the smart home automation scene or service update. Call home_assistant_services call_service to trigger lighting, climate, script, or custom notification actions matching the target schedule and state.
Expected: `automation_results, service_call_logs`

### Step 2: KG Persistence [depends_on: Step 0, Step 1]
**Agent**: `deployer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `list_states` returns nothing | Home Assistant URL or token is not configured | Set the Home Assistant URL and long-lived token in the agent environment and call `home_assistant_states` again. |
| `call_service` is rejected | Wrong domain, service name or entity id | Look up the entity in `list_states`, correct the service data, and call `home_assistant_services` with it. |
| Entity state does not change | Device is offline or unavailable | Check the entity state for `unavailable`, restore the device connection, and re-run the service call. |

## Output
- Smart Home Automation Orchestrator results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — collect-home-state; Step 1 — execute-home-automation
- **After level 0:** Step 2 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
