---
name: confluence-knowledge-ingester
description: >-
  Fetches a Confluence wiki page, saves it locally as a standard markdown file, and pre-stages the artifact for seamless Knowledge Graph ingestion.
domain: ops
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
tags: ['atlassian', 'confluence', 'wiki', 'knowledge-base', 'atlassian-agent', 'graph-os']
concept: CONCEPT:KG-2.12
---

# Confluence Knowledge Ingester Workflow

**CONCEPT:KG-2.12**

Fetches a Confluence wiki page, saves it locally as a standard markdown file, and pre-stages the artifact for seamless Knowledge Graph ingestion.

## Steps

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

### Step 2: Graph Os
**Agent**: `validator-agent`
**Tools**: `graph_query`

Write the formatted page content to save_path and call mcp_graph-os_graph_ingest tool with the target path to natively ingest the Confluence document into the Knowledge Graph.
Expected: `ingestion_job_status`

### Step 3: KG Persistence [depends_on: graph-os]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Confluence Knowledge Ingester results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Atlassian Agent; Step 1 — User Interaction; Step 2 — Graph Os
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
