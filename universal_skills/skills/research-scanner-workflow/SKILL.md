---
name: research-scanner-workflow
skill_type: workflow
description: >-
  Discover research papers using ScholarX and bulk ingest them into the Arbora Knowledge Graph
domain: development-workflows
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
metadata:
  version: '1.7.0'
---

# Research Scanner Workflow

**CONCEPT:DEV-001**

Discover research papers using ScholarX and bulk ingest them into the Arbora Knowledge Graph

## Steps

1. Ask the user for the research focus (`query`), lookback days, target sources and maximum results. Verify that each of those four parameters is stated before searching.
2. Search papers with `scholarx_search` using `action='search'`. Verify that the results list matches the requested sources and lookback window.
3. Submit the discovered paper IDs with `scholarx_download_papers` and poll `action='status'`. Verify that the queue status shows every ID as downloaded.
4. Ingest the PDFs into the Knowledge Graph with `mcp_arbora_graph_ingest` using `action='ingest'`. Verify that the ingest result reports the number of documents added.
5. Show the research summary and ingested paper details to the user as the `present-research-summary` output. Verify that each ingested paper appears in the summary.
6. Persist the results as typed nodes and edges with `graph_write`. Verify that a follow-up `graph_query` returns the new nodes linked to existing domain entities.

### Step 0: collect-research-request [skill: user-interaction]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Get the user's research focus query, lookback days, specific target scientific sources (e.g., arxiv, biorxiv), and maximum results.

### Step 1: search-papers [skill: scholarx-mcp]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Search for the research papers based on the search parameters using the `scholarx_search` action with `action='search'`.

### Step 2: download-papers [skill: scholarx-mcp]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Submit bulk download jobs for the discovered paper IDs via `scholarx_download_papers`. Check the download queue status via `action='status'`.

### Step 3: Arbora
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Ingest the newly downloaded research PDFs into the Knowledge Graph via the ingest action `mcp_arbora_graph_ingest` with `action='ingest'`.

### Step 4: present-research-summary [skill: user-interaction]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Display the completed research summary and details of the ingested papers to the user.

### Step 5: KG Persistence [depends_on: Step 0, Step 4]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Search returns no papers | The query or lookback window is too narrow | Widen the query or increase the lookback days and call `scholarx_search` again. |
| Downloads stay queued | The download queue is stalled | Check `action='status'`, remove failed IDs, and resubmit them with `scholarx_download_papers`. |
| Ingest reports zero documents | The PDFs were not downloaded or are unreadable | Confirm the downloads finished with `action='status'` before calling `mcp_arbora_graph_ingest` again. |
| `graph_write` persistence is rejected | A node has no type or no link target | Re-issue `graph_write` with a typed node and an edge to an entity located first with `graph_query`. |

## Output
- Research Scanner results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — collect-research-request; Step 1 — search-papers; Step 2 — download-papers; Step 3 — Arbora; Step 4 — present-research-summary
- **After level 0:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
