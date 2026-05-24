---
name: confluence_knowledge_ingester
description: Fetches a Confluence wiki page, saves it locally as a standard markdown file, and pre-stages the artifact for seamless Knowledge Graph ingestion.
domain: ops
tags: ['atlassian', 'confluence', 'wiki', 'knowledge-base', 'atlassian-agent', 'graph-os']
requires: ['atlassian-agent', 'graph-os']
---

# confluence_knowledge_ingester Workflow

Fetches a Confluence wiki page, saves it locally as a standard markdown file, and pre-stages the artifact for seamless Knowledge Graph ingestion.

### Step 0: atlassian-agent
Retrieve a Confluence page's HTML or wiki content by ID or space key and title using the atlassian_confluence_page tool.
Expected: confluence_page_data

### Step 1: user-interaction
Present the fetched Confluence page content summary. Prompt the user for a preferred saving path in the workspace for markdown conversion and future ingestion.
Expected: save_path, file_metadata
Depends On: Step 0

### Step 2: graph-os
Write the formatted page content to save_path and call mcp_graph-os_graph_ingest tool with the target path to natively ingest the Confluence document into the Knowledge Graph.
Expected: ingestion_job_status
Depends On: Step 1
