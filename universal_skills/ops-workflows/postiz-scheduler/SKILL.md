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
  version: '1.1.0'
---

# Postiz Scheduler Workflow

**CONCEPT:KG-2.12**

Automatically lists active social integrations, discovers slot availabilities, prompts the user for text/media content, and schedules posts via the Postiz MCP server.

## Steps

### Step 0: Postiz Agent
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Retrieve active integration accounts and check for slot time recommendations using postiz_integrations with list_integrations or check_connection actions.
Expected: `active_integrations, recommended_slots`

### Step 1: User Interaction
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Present active channels and slot suggestions. Prompt the user for post body text, image/video attachment URLs, and schedule parameters.
Expected: `post_content, file_url, release_time`

### Step 2: Postiz Agent
**Agent**: `validator-agent`
**Tools**: `graph_query`

Create and schedule the post (uploading the file attachment if provided) using the postiz_posts and postiz_uploads tools.
Expected: `post_creation_result`

### Step 3: KG Persistence [depends_on: postiz-agent]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Postiz Scheduler results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Postiz Agent; Step 1 — User Interaction; Step 2 — Postiz Agent
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
