---
name: research-scanner
domain: research
skill_type: skill
description: >-
  Discover research papers: extract focus topics from the Knowledge Graph, build a relevance taxonomy, fetch daily papers via the scholarx MCP, sweep web and social sources via PulseLink, score locally, and ingest the best. Use when asked to scan for papers, find new research, or check arxiv. Do NOT use to analyze a single known paper (comparative-analysis).
license: MIT
tags: [research, scanner, scholarx, pulselink, automation, agent-workflow]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---

# Research Scanner Skill

Scope: Agentic research paper discovery pipeline. Extracts focus topics from the Knowledge Graph, dynamically builds a relevance taxonomy, fetches daily papers via the scholarx MCP, and also sweeps open-web and social sources (Hacker News, Reddit, X, YouTube, news, web) via the PulseLink MCP, scores them locally, and ingests the most valuable items. Triggers on "scan for papers", "find new research", "check arxiv", "research scan", proactively discover research that could enhance a codebase.

Automated research paper discovery, dynamic relevance scoring, and integration pipeline.

## Overview

Unlike static scanners, the Research Scanner is an **agent-driven workflow**. It dynamically extracts active codebases, architectural concepts, and areas of focus from the `meristem-kg` Knowledge Graph, formulates a targeted taxonomy, and fetches the latest papers using the `scholarx` MCP server.

This skill orchestrates multiple atomic MCP tools to create a resilient, rate-limited, and context-aware research discovery pipeline.

## Steps

1. Query the Knowledge Graph for focus topics with `mcp_meristem-kg_kg_query` using `MATCH (c:ConceptNode) RETURN c.id, c.description LIMIT 10`. Verify that at least one concept row returns, since an empty result means the graph is not ingested.
2. Fetch recent papers with the `scholarx` tool `get_recent_papers` and save the JSON to `papers.json`. Verify that `python3 -c "import json;print(len(json.load(open('papers.json'))))"` prints a count above zero.
3. Optionally sweep reach sources with `pulse_status()` followed by `pulse_search(source="hackernews", query=<topic>)`. Verify that `pulse_status()` reports the chosen source as ready before trusting empty results.
4. Score the papers with `python scripts/dynamic_scorer.py --papers papers.json --min-score 3.0 --output top_papers.json`. Verify that `top_papers.json` exists and lists the IDs that cleared the minimum score.
5. Deduplicate against the graph with `kg_search` and queue the new IDs with the `scholarx` download tool. Verify that `list_downloads` shows each new ID as queued or complete.
6. Ingest the downloaded files with `mcp_meristem-kg_kg_ingest`. Verify that a `kg_search` for one ingested paper title returns its `Document` node.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `get_recent_papers` returns an empty list | The RSS window (`days=1`) had no new papers, or the `scholarx` server is down | Call `search_papers` with a topic from Step 1 of the Steps list, or widen `days`, and confirm the server answers a `list_downloads` call |
| `dynamic_scorer.py` writes an empty `top_papers.json` | `--min-score 3.0` is too strict, or the taxonomy detection found no graph nodes | Lower `--min-score` (for example 1.5) and check `references/relevance_taxonomy.json` exists as the fallback taxonomy |
| `pulse_search` fails for X or Reddit | The source needs a credential that is not configured in the shared credential provider | Run `pulse_status()`, use only sources it reports as ready (hackernews, web, news), and ask the operator to configure the credential |
| `kg_ingest` rejects the files | The downloads were still running, so the files were incomplete | Wait until `download_status` reports completion, then ingest again |

## Workflow Execution Steps

When triggered to perform a daily scan or research sweep, follow these steps exactly:

### Step 2: Extract Topics from the Knowledge Graph
Identify what the project currently cares about by querying the KG.
Use `mcp_meristem-kg_kg_query` to fetch relevant domains to get a sense of what's there (Optional context for your reasoning).
*Example queries:*
- Fetch active codebases/pillars: `MATCH (c:CodeNode) RETURN c.name, c.description LIMIT 10`
- Fetch core architectural concepts: `MATCH (c:ConceptNode) RETURN c.id, c.description LIMIT 10`

### Step 3: Fetch Recent Papers
Use the `scholarx` MCP tool `get_recent_papers` to fetch the latest papers (via RSS if `days=1`).
Save the resulting JSON output to a local file, e.g., `papers.json`.

*Note: For targeted searches, you can use the `search_papers` tool instead.*

### Step 3b: Broaden beyond papers — PulseLink reach sources (optional, on by default)
Research is not only arXiv. For the same focus topics, also sweep the open web and
social/community sources via the **PulseLink** MCP server (`pulselink-mcp`, the
keyless-first sibling to `scholarx`). Use its tools to gather discussion, talks, and
news that papers miss:
- `pulse_search(source="hackernews"|"reddit"|"x"|"github"|"news"|"web", query=<topic>)`
  — normalized `{documents:[{id,title,url,text,author,created_at,metrics}], next_cursor}`.
- `pulse_fetch(source, target)` for full text/threads; `pulse_transcribe(target)` for a
  YouTube talk transcript.
- `pulse_status()` first to see which sources are live (keyless sources are always
  ready; X/Reddit/LinkedIn light up only when a credential is configured).

Keyless sources (hackernews, web, news, youtube, rss, v2ex, bilibili) need **zero**
setup. Auth-walled sources authenticate through the shared credential provider — no
keys go in this skill.

### Step 4: Score the Papers Dynamically
Use the provided `scripts/dynamic_scorer.py` to evaluate the fetched papers. The script will automatically auto-detect the meristem KG and construct a taxonomy dynamically without needing hardcoded files!

```bash
python ${MERISTEM_WORKSPACE_ROOT}/agent-packages/skills/universal-skills/universal_skills/skills/research-scanner/scripts/dynamic_scorer.py \
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
Once downloaded, perform a "double-write" by invoking `mcp_meristem-kg_kg_ingest` on the newly downloaded PDFs/markdown files to store them permanently in the Knowledge Graph for other agents to discover.

For PulseLink reach sources (Step 3b), ingest declaratively via the `mcp_tool` source
presets (`pulselink-hackernews`, `pulselink-reddit`, `pulselink-x`, `pulselink-youtube`,
`pulselink-web`, `pulselink-news`, `pulselink-github`, `pulselink-rss`, `pulselink-v2ex`,
… — see `meristem` `MCP_TOOL_PRESETS`). Each fetched item then becomes a
first-class KG `Document` (chunked, embedded, deduplicated, ACL'd) — the same pipeline
as papers — so `deep-research` and other agents can synthesize across papers **and**
open-web/social evidence together. Example: ingest with
`{"content_type": "connector", "connector": {"source_type": "mcp_tool", "preset": "pulselink-hackernews", "params": {"query": "<topic>"}}}`.
