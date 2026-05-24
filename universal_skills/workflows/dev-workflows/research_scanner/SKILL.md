---
name: research_scanner
description: Discover research papers using ScholarX and bulk ingest them into the Graph-OS Knowledge Graph
tags:
  - dev-workflows
  - research
  - knowledge-graph
requires:
  - scholarx-mcp
  - graph-os
---

# Research Scanner Workflow

Discover relevant daily research papers across configured scientific repositories and bulk ingest them directly into the Graph-OS Knowledge Graph.

## Steps

### Step 0: user-interaction
Get the user's research focus query, lookback days, specific target scientific sources (e.g., arxiv, biorxiv), and maximum results.

### Step 1: scholarx-mcp
Search for the research papers based on the search parameters using the `scholarx_search` action with `action='search'`.

### Step 2: scholarx-mcp
Submit bulk download jobs for the discovered paper IDs via `scholarx_storage` with `action='bulk_download'`. Check the download queue status via `action='status'`.

### Step 3: graph-os
Ingest the newly downloaded research PDFs into the Knowledge Graph via the ingest action `mcp_graph-os_graph_ingest` with `action='ingest'`.

### Step 4: user-interaction
Display the completed research summary and details of the ingested papers to the user.
