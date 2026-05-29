---
name: research-scanner
description: >-
  Agentic research paper discovery pipeline. Extracts focus topics from the Knowledge Graph,
  dynamically builds a relevance taxonomy, fetches daily papers via the scholarx MCP,
  scores them locally, and bulk downloads the most valuable papers for ingestion.
  Triggers on "scan for papers", "find new research", "check arxiv", "research scan",
  proactively discover research that could enhance a codebase.
license: MIT
tags: [research, scanner, scholarx, automation, agent-workflow]
metadata:
  author: Genius
  version: '0.24.0'
---

# Research Scanner Skill

Automated research paper discovery, dynamic relevance scoring, and integration pipeline.

## Overview

Unlike static scanners, the Research Scanner is an **agent-driven workflow**. It dynamically extracts active codebases, architectural concepts, and areas of focus from the `agent-utilities-kg` Knowledge Graph, formulates a targeted taxonomy, and fetches the latest papers using the `scholarx` MCP server.

This skill orchestrates multiple atomic MCP tools to create a resilient, rate-limited, and context-aware research discovery pipeline.

## Workflow Execution Steps

When triggered to perform a daily scan or research sweep, follow these steps exactly:

### Step 2: Extract Topics from the Knowledge Graph
Identify what the project currently cares about by querying the KG.
Use `mcp_agent-utilities-kg_kg_query` to fetch relevant domains to get a sense of what's there (Optional context for your reasoning).
*Example queries:*
- Fetch active codebases/pillars: `MATCH (c:CodeNode) RETURN c.name, c.description LIMIT 10`
- Fetch core architectural concepts: `MATCH (c:ConceptNode) RETURN c.id, c.description LIMIT 10`

### Step 3: Fetch Recent Papers
Use the `scholarx` MCP tool `get_recent_papers` to fetch the latest papers (via RSS if `days=1`).
Save the resulting JSON output to a local file, e.g., `papers.json`.

*Note: For targeted searches, you can use the `search_papers` tool instead.*

### Step 4: Score the Papers Dynamically
Use the provided `scripts/dynamic_scorer.py` to evaluate the fetched papers. The script will automatically auto-detect the agent-utilities KG and construct a taxonomy dynamically without needing hardcoded files!

```bash
python /home/apps/workspace/agent-packages/skills/universal-skills/universal_skills/research/research-scanner/scripts/dynamic_scorer.py \
    --papers papers.json \
    --min-score 3.0 \
    --output top_papers.json
```
This script will evaluate keyword density against all active graph nodes and output the IDs of the top-scoring papers into `top_papers.json`.

### Step 5: Deduplicate and Bulk Download
Read the IDs from `top_papers.json`. Check if they already exist in the KG using `kg_search` or `kg_query`.
For the new, highly-relevant IDs, queue them for background downloading using the `scholarx` MCP tool:
```json
{
  "source": "arxiv",
  "paper_ids": "2605.04050,2605.04107"
}
```
*Note: Use `list_downloads` and `download_status` to monitor the queue.*

### Step 6: Ingest into the Knowledge Graph
Once downloaded, perform a "double-write" by invoking `mcp_agent-utilities-kg_kg_ingest` on the newly downloaded PDFs/markdown files to store them permanently in the Knowledge Graph for other agents to discover.
