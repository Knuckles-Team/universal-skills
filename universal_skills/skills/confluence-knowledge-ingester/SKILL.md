---
name: confluence-knowledge-ingester
skill_type: workflow
description: >-
  Fetches a Confluence wiki page, saves it locally as a standard markdown file, and pre-stages the artifact for seamless Knowledge Graph ingestion.
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
tags: ['atlassian', 'confluence', 'wiki', 'knowledge-base', 'atlassian-agent', 'arbora']
concept: CONCEPT:KG-2.12
metadata:
  version: '1.7.0'
---

# Confluence Knowledge Ingester Workflow

**CONCEPT:KG-2.12**

Fetches a Confluence wiki page, saves it locally as a standard markdown file, and pre-stages the artifact for seamless Knowledge Graph ingestion.

## Steps

1. Fetch the Confluence page by ID or by space key and title with the `atlassian_confluence_page` tool (Step 0). Verify that `confluence_page_data` contains the page title and a non-empty body.
2. Present the page summary to the user and ask for a save path in the workspace (Step 1). Verify that `save_path` is a writable workspace path whose parent exists per `ls`.
3. Write the markdown to `save_path` and ingest it with `mcp_arbora_graph_ingest` (Step 2). Verify that the file exists and that `ingestion_job_status` reports success.
4. Persist the typed nodes and edges for the ingested page with `graph_write` (Step 3). Verify that `graph_query` returns the new page node with its source link.

### Step 0: Atlassian Agent
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Retrieve a Confluence page's HTML or wiki content by ID or space key and title using the atlassian_confluence_page tool.
Expected: `confluence_page_data`

### Step 1: User Interaction
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Present the fetched Confluence page content summary. Prompt the user for a preferred saving path in the workspace for markdown conversion and future ingestion.
Expected: `save_path, file_metadata`

### Step 2: Arbora
**Agent**: `validator-agent`
**Tools**: `graph_query`

Write the formatted page content to save_path and call mcp_arbora_graph_ingest tool with the target path to natively ingest the Confluence document into the Knowledge Graph.
Expected: `ingestion_job_status`

### Step 3: KG Persistence [depends_on: arbora]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| `atlassian_confluence_page` returns 404 or empty content | Wrong page ID or space key, or the account lacks view access | Re-resolve the page by space key and title, confirm the account permissions in Confluence, and call the tool again with the corrected identifier |
| Save path rejected | The chosen directory is outside the workspace or missing | Create the directory with `mkdir -p` inside the workspace and pass the new path to Step 2 |
| `ingestion_job_status` shows failed | The markdown has malformed front-matter or arbora is down | Open the saved file and fix the front-matter, check arbora with `graph_query`, and call `mcp_arbora_graph_ingest` on the path again |


## Output
- Confluence Knowledge Ingester results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Atlassian Agent; Step 1 — User Interaction; Step 2 — Arbora
- **After level 0:** Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
