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
  version: '1.2.1'
---

# Smart Home Automation Orchestrator Workflow

**CONCEPT:INFRA-001**

Interacts with Home Assistant using home-assistant-agent to read device states, query calendar schedules, and trigger specific smart home services, scenes, scripts, or events.

## Steps

### Step 0: Home Assistant Agent
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Retrieve current device states, entity metrics, and active calendar event triggers using home_assistant_states list_states and home_assistant_calendar get_calendar_events tools. Target sensor context: {{task}}
Expected: `sensor_states, calendar_schedules, target_devices`

### Step 1: Home Assistant Agent
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute the smart home automation scene or service update. Call home_assistant_services call_service to trigger lighting, climate, script, or custom notification actions matching the target schedule and state.
Expected: `automation_results, service_call_logs`

### Step 2: KG Persistence [depends_on: home-assistant-agent]
**Agent**: `deployer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Smart Home Automation Orchestrator results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Home Assistant Agent; Step 1 — Home Assistant Agent
- **After level 0:** Step 2 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
