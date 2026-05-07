---
name: research-scanner
description: >-
  Periodically scan academic paper sources (arXiv, PMC, bioRxiv, Semantic Scholar)
  for new research, score relevance against a target codebase or concept taxonomy,
  filter out low-value papers, and download the valuable ones for comparative
  analysis. Uses the ScholarX MCP server for paper search and download. Triggers
  on "scan for papers", "find new research", "check arxiv", "research scan",
  "paper discovery", "what's new in AI research", or when the agent needs to
  proactively discover research that could enhance a codebase. Do NOT use for
  general web search — use web-search instead.
license: MIT
tags: [arxiv, research, papers, scholarx, mcp, discovery, relevance-scoring]
metadata:
  author: Genius
  version: '0.8.0'
---

# Research Scanner

Automated research paper discovery, relevance scoring, and download pipeline powered
by the ScholarX MCP server. Designed for periodic invocation to keep a local research
library current with the latest publications relevant to a target domain.

## Overview

Research Scanner connects to the ScholarX MCP server to:
1. **Fetch** recent papers from academic sources (arXiv, PMC, bioRxiv, etc.)
2. **Score** each paper's abstract against a configurable relevance taxonomy
3. **Filter** out irrelevant papers (junk) to save compute and storage
4. **Download** PDFs for accepted papers with rate-limiting and retry
5. **Report** relevance rankings and domain-matched concepts

## Prerequisites

The ScholarX MCP server must be accessible. Load it into the agent's MCP config:

```json
{
  "mcpServers": {
    "scholarx": {
      "command": "scholarx-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "SEARCHTOOL": "True",
        "DISCOVERYTOOL": "True",
        "STORAGETOOL": "True"
      }
    }
  }
}
```

Or use the mcp-client skill to connect:
```bash
python scripts/mcp_client.py \
    --config scholarx/mcp_config.json \
    --server scholarx \
    --action call-mcp-tool \
    --tool-name search_papers \
    --tool-args '{"query": "multi-agent systems", "categories": "cs.AI", "max_results": 30}'
```

## Workflow

### Phase 1: Fetch Papers

Use the ScholarX MCP `search_papers` tool or `get_recent_papers` tool:

```bash
# Via mcp-client
python -m universal_skills.skills.mcp-client.scripts.mcp_client \
    --config <scholarx-mcp-config> --server scholarx \
    --action call-mcp-tool \
    --tool-name search_papers \
    --tool-args '{"query": "artificial intelligence", "sources": "arxiv", "categories": "cs.AI,cs.MA,cs.LG", "max_results": 30, "sort_by": "date"}'
```

Or use the standalone script:
```bash
python scripts/relevance_scanner.py \
    --query "artificial intelligence" \
    --categories cs.AI,cs.MA,cs.LG \
    --max-results 30 \
    --target-project /path/to/codebase \
    --output-dir /path/to/paper/library
```

### Phase 2: Score Relevance

The `relevance_scanner.py` script scores each paper against a taxonomy of weighted
keywords organized by domain. Domains and weights are configurable via the
`references/relevance_taxonomy.json` file.

Default domains (from agent-utilities ecosystem):

| Domain | Weight | Example Keywords |
|--------|--------|-----------------|
| Orchestration | 3.0 | multi-agent, workflow, agentic, task decomposition |
| Knowledge Graph | 3.0 | knowledge graph, ontology, OWL, entity relation |
| Planning & Reasoning | 2.5 | chain of thought, MCTS, planning, deliberation |
| Memory & Retrieval | 2.5 | RAG, episodic memory, continual learning |
| Tool Use | 2.0 | function calling, MCP, code generation |
| Evaluation & Safety | 2.0 | benchmark, red team, alignment, hallucination |
| Swarm & Evolution | 2.0 | evolutionary, swarm, ant colony, stigmergy |
| LLM Architecture | 1.5 | transformer, MoE, distillation, quantization |
| Human-AI | 1.0 | human-in-the-loop, conversational, dialogue |

### Phase 3: Filter & Accept

Papers are classified into three tiers:

| Verdict | Score | Action |
|---------|-------|--------|
| ✅ Relevant | ≥ 3.0 | Accept — direct value for target domain |
| 🟡 Marginal | 1.0–2.9 | Accept — small value could unlock bigger value later |
| ❌ Irrelevant | < 1.0 | Reject — no domain overlap detected |

### Phase 4: Download with Rate Limiting

Accepted papers are downloaded with:
- **3.5s delay** between requests (arXiv's 1-req/3s policy + safety margin)
- **3 retries** with exponential backoff (5s, 10s, 20s)
- **Deduplication** — already-downloaded papers are skipped automatically

### Phase 5: Report

Output files:
- `relevance_scores.json` — Full scoring breakdown for all fetched papers
- `paper_XX.md` — Markdown summaries with abstracts and relevance analysis
- `papers_metadata.json` — Machine-readable metadata for accepted papers
- `pdfs/` — Downloaded PDF files

## Incremental Mode

On subsequent runs, the scanner automatically skips already-downloaded papers.
Use the ScholarX MCP `get_stored_papers` tool to check what's already in the library:

```bash
python -m universal_skills.skills.mcp-client.scripts.mcp_client \
    --config <scholarx-mcp-config> --server scholarx \
    --action call-mcp-tool \
    --tool-name get_stored_papers --tool-args '{}'
```

## Customizing the Taxonomy

Edit `references/relevance_taxonomy.json` to customize domains and keywords for
your specific project. Each domain has:
- `weight` (float) — Multiplier for domain relevance (higher = more important)
- `keywords` (list) — Substring matches against title + abstract

## Integration with Comparative Analysis

After scanning, feed accepted papers into the `comparative-analysis` skill:
```bash
python scripts/extract_innovations.py \
    --source /path/to/paper_library/paper_01.md \
    --target /path/to/codebase
```

## Best Practices

- **Run periodically** — Weekly or daily scans catch new publications quickly
- **Tune the taxonomy** — Add project-specific keywords to reduce false negatives
- **Start broad, refine later** — A marginal paper today may spark a breakthrough tomorrow
- **Combine with comparative-analysis** — Use innovation extraction to find actionable synergies
- **Monitor rate limits** — The scanner respects source rate limits, but very large batches
  (>100 papers) may take several minutes for PDF downloads

## Bundled Resources

### Scripts
- `scripts/relevance_scanner.py` — Standalone relevance-scored paper pipeline

### References
- `references/relevance_taxonomy.json` — Configurable domain taxonomy with weights
