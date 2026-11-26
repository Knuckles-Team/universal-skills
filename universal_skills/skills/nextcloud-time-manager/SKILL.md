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
  version: '1.6.2'
---

# Nextcloud Time Manager Workflow

**CONCEPT:KG-2.12**

Connects to Nextcloud using nextcloud-agent, retrieves latest calendar events and task files, interacts with the user to discover scheduling modifications, and applies updates/adds/removes to synchronize their personal schedule.

## Steps

1. Retrieve calendars and tasks with `nextcloud_calendar` `list_calendars`, `list_calendar_events` and `nextcloud_files` `list_files`. Verify that `calendars`, `events` and `tasks` are returned.
2. Summarize the schedule to the user and ask for changes. Verify that `user_schedule_instructions` is recorded with the user's confirmation.
3. Apply changes with `nextcloud_calendar` `create_calendar_event` and `nextcloud_files` write tools. Verify that re-listing with `list_calendar_events` shows the change.
4. Persist the results with `graph_write`. Verify that a `graph_query` returns the new nodes.

### Step 0: Nextcloud Schedule Retrieval [skill: nextcloud-agent]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Retrieve current calendar lists and schedule events using nextcloud_calendar list_calendars and list_calendar_events tools. Fetch active tasks using nextcloud_files list_files in the task directory.
Expected: `calendars, events, tasks`

### Step 1: User Interaction
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Analyze the retrieved calendar events and tasks. Present a summary of the current schedule to the user, and prompt them to specify any new events/tasks to add, modify, or remove.
Expected: `user_schedule_instructions`

### Step 2: Nextcloud Schedule Mutation [skill: nextcloud-agent]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Apply requested scheduling modifications to Nextcloud. Call nextcloud_calendar create_calendar_event to register new events, or call nextcloud_files tools to write/update/delete task records as instructed.
Expected: `nextcloud_sync_results`

### Step 3: KG Persistence [depends_on: Step 2]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Calendar list is empty | Wrong Nextcloud credentials | Check the nextcloud-agent credentials and reconnect |
| Event not created | Invalid date format | Use ISO 8601 times and call `create_calendar_event` again |
| Duplicate tasks | Mutation applied twice | List with `list_files` first and update the existing record |

## Output
- Nextcloud Time Manager results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Nextcloud Schedule Retrieval; Step 1 — User Interaction; Step 2 — Nextcloud Schedule Mutation
- **After level 0:** Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
