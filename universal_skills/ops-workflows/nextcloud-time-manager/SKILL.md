---
name: nextcloud-time-manager
skill_type: workflow
description: >-
  Connects to Nextcloud using nextcloud-agent, retrieves latest calendar events and task files, interacts with the user to discover scheduling modifications, and applies updates/adds/removes to synchronize their personal schedule.
domain: ops-workflows
agent: operations_coordinator
team_config:
  name: operations_team
  task_pattern: operational process coordination
  execution_mode: sequential
  specialist_ids:
    - intake-agent
    - processor-agent
    - validator-agent
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
    validator-agent: [graph_query]
tags: ['nextcloud', 'calendar', 'tasks', 'personal-assistant', 'nextcloud-agent']
concept: CONCEPT:KG-2.12
metadata:
  version: '1.1.0'
---

# Nextcloud Time Manager Workflow

**CONCEPT:KG-2.12**

Connects to Nextcloud using nextcloud-agent, retrieves latest calendar events and task files, interacts with the user to discover scheduling modifications, and applies updates/adds/removes to synchronize their personal schedule.

## Steps

### Step 0: Nextcloud Agent
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Retrieve current calendar lists and schedule events using nextcloud_calendar list_calendars and list_calendar_events tools. Fetch active tasks using nextcloud_files list_files in the task directory.
Expected: `calendars, events, tasks`

### Step 1: User Interaction
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Analyze the retrieved calendar events and tasks. Present a summary of the current schedule to the user, and prompt them to specify any new events/tasks to add, modify, or remove.
Expected: `user_schedule_instructions`

### Step 2: Nextcloud Agent
**Agent**: `validator-agent`
**Tools**: `graph_query`

Apply requested scheduling modifications to Nextcloud. Call nextcloud_calendar create_calendar_event to register new events, or call nextcloud_files tools to write/update/delete task records as instructed.
Expected: `nextcloud_sync_results`

### Step 3: KG Persistence [depends_on: nextcloud-agent]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Nextcloud Time Manager results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Nextcloud Agent; Step 1 — User Interaction; Step 2 — Nextcloud Agent
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
