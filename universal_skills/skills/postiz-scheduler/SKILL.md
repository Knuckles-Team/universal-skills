---
name: postiz-scheduler
skill_type: workflow
description: >-
  Automatically lists active social integrations, discovers slot availabilities, prompts the user for text/media content, and schedules posts via the Postiz MCP server.
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
tags: ['postiz', 'social-media', 'marketing', 'scheduling', 'postiz-agent']
concept: CONCEPT:KG-2.12
metadata:
  version: '1.6.2'
---

# Postiz Scheduler Workflow

**CONCEPT:KG-2.12**

Automatically lists active social integrations, discovers slot availabilities, prompts the user for text/media content, and schedules posts via the Postiz MCP server.

## Steps

1. List active integrations and recommended slots with `postiz_integrations` using the `list_integrations` or `check_connection` actions. Verify that `active_integrations` is non-empty.
2. Collect the post body, media URLs and schedule from the user after presenting the channels and slots. Verify that `post_content` and `release_time` are provided and the user approved them.
3. Create and schedule the post with `postiz_posts` and `postiz_uploads`. Verify that `post_creation_result` contains a post identifier and the scheduled time.
4. Persist the results as typed nodes and edges with `graph_write`. Verify that a follow-up `graph_query` returns the new nodes linked to existing domain entities.

### Step 0: Postiz Integration Discovery [skill: postiz-agent]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Retrieve active integration accounts and check for slot time recommendations using postiz_integrations with list_integrations or check_connection actions.
Expected: `active_integrations, recommended_slots`

### Step 1: User Interaction
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Present active channels and slot suggestions. Prompt the user for post body text, image/video attachment URLs, and schedule parameters.
Expected: `post_content, file_url, release_time`

### Step 2: Postiz Post Scheduling [skill: postiz-agent]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Create and schedule the post (uploading the file attachment if provided) using the postiz_posts and postiz_uploads tools.
Expected: `post_creation_result`

### Step 3: KG Persistence [depends_on: Step 2]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| No active integrations returned | The channel connection expired | Reconnect the channel in Postiz and confirm it with `postiz_integrations` using `check_connection`. |
| Media upload fails | The file URL is unreachable or the format is unsupported | Provide a reachable URL in a supported format and repeat the upload with `postiz_uploads`. |
| Post scheduled in the past | The `release_time` is earlier than the current time | Ask the user for a future time from the recommended slots and schedule again with `postiz_posts`. |
| `graph_write` persistence is rejected | A node has no type or no link target | Re-issue `graph_write` with a typed node and an edge to an entity located first with `graph_query`. |

## Output
- Postiz Scheduler results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Postiz Integration Discovery; Step 1 — User Interaction; Step 2 — Postiz Post Scheduling
- **After level 0:** Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
