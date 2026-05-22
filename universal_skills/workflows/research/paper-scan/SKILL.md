---
name: paper-scan
description: >-
  Extracts focus topics, fetches daily papers, scores them, and downloads the most valuable papers.
tags: [research, scan, arxiv, papers]
metadata:
  author: agent-utilities
  version: '1.0.0'
---
# Paper Scan Workflow

> [!NOTE]
> This workflow was migrated from the legacy WorkflowBundle preset system.

## Workflow Execution Steps

### Step 1: topic-extractor
Extract focus topics from the Knowledge Graph to build a relevance taxonomy.

### Step 2: scholarx-fetcher
Fetch daily papers via the scholarx MCP using the extracted taxonomy.

### Step 3: paper-scorer
Score the fetched papers locally against the relevance taxonomy.

### Step 4: paper-downloader
Bulk download the most valuable papers for ingestion.
