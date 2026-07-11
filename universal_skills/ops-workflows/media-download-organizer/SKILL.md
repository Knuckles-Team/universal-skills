---
name: media-download-organizer
skill_type: workflow
description: >-
  Parallel execution workflow for media download organizer using the Unified Parallel Engine
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
    - report-agent
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
    validator-agent: [graph_query]
    report-agent: [graph_write, document_tools]
tags: [ops, media-download-organizer]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.2.0'
---

# Media Download Organizer Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for media download organizer using the Unified Parallel Engine

## Steps

### Step 1: Search
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute search operations for the Media Download Organizer workflow.
Expected: `search_artifacts`

### Step 2: Download [depends_on: search]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute download operations for the Media Download Organizer workflow.
Expected: `download_artifacts`

### Step 3: Organize [depends_on: download]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute organize operations for the Media Download Organizer workflow.
Expected: `organize_artifacts`

### Step 4: Add To Library [depends_on: organize]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute add to library operations for the Media Download Organizer workflow.
Expected: `add_to_library_artifacts`

### Step 5: Clean Up [depends_on: add_to_library]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute clean up operations for the Media Download Organizer workflow.
Expected: `clean_up_artifacts`

### Step 6: KG Persistence [depends_on: clean_up]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Media Download Organizer results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Search
- **After level 0:** Step 2 — Download
- **After level 1:** Step 3 — Organize
- **After level 2:** Step 4 — Add To Library
- **After level 3:** Step 5 — Clean Up
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
