---
name: research_scanner
description: >-
  Discover research papers using ScholarX and bulk ingest them into the Graph-OS Knowledge Graph
domain: dev-workflows
agent: dev_ops_engineer
team_config:
  name: development_operations_team
  task_pattern: development workflow automation
  execution_mode: parallel
  specialist_ids:
    - scanner-agent
    - builder-agent
    - validator-agent
    - publisher-agent
  tool_assignments:
    scanner-agent: [rep_rm_workspace, rep_rm_git]
    builder-agent: [rep_rm_projects]
    validator-agent: [rep_rm_projects, gl_pipelines]
    publisher-agent: [rep_rm_git, gl_merge_requests]
tags: [dev-workflows, research-scanner]
concept: CONCEPT:DEV-001
---

# Research Scanner Workflow

**CONCEPT:DEV-001**

Discover research papers using ScholarX and bulk ingest them into the Graph-OS Knowledge Graph

## Steps

### Step 0: User Interaction
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Get the user's research focus query, lookback days, specific target scientific sources (e.g., arxiv, biorxiv), and maximum results.

### Step 1: Scholarx Mcp
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Search for the research papers based on the search parameters using the `scholarx_search` action with `action='search'`.

### Step 2: Scholarx Mcp
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Submit bulk download jobs for the discovered paper IDs via `scholarx_storage` with `action='bulk_download'`. Check the download queue status via `action='status'`.

### Step 3: Graph Os
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Ingest the newly downloaded research PDFs into the Knowledge Graph via the ingest action `mcp_graph-os_graph_ingest` with `action='ingest'`.

### Step 4: User Interaction
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Display the completed research summary and details of the ingested papers to the user.

### Step 5: KG Persistence [depends_on: user-interaction]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Research Scanner results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
