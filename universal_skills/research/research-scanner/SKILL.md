---
name: research-scanner
description: >-
  Periodically scan academic paper sources (arXiv, PMC, bioRxiv, Semantic Scholar)
  for new research, score relevance against a target codebase or concept taxonomy,
  filter out low-value papers, and download the valuable ones for comparative analysis.
  Uses the ScholarX library for paper discovery, scoring, and download.
  Triggers on "scan for papers", "find new research", "check arxiv", "research scan",
  "paper discovery", "what's new in AI research", or when the agent needs to
  proactively discover research that could enhance a codebase.
  Do NOT use for general web search — use web-search instead.
license: MIT
tags: [research, scanner, scholarx, automation]
metadata:
  author: Genius
  version: '0.9.0'
---

# Research Scanner

Automated research paper discovery, relevance scoring, and integration pipeline.

## Overview

The Research Scanner provides two scanning modes:

1. **Daily RSS Scan** — Fetches today's papers from arXiv RSS feeds, scores relevance
   against a configurable taxonomy, filters out irrelevant papers, downloads top-scored
   PDFs, and generates a synergy report.

2. **Query-Based Search** — Searches for papers using the ScholarX API, scores and
   filters results, and produces reports for targeted research discovery.

Both modes use the `scholarx.scanner` library as their engine.

## Quick Start

### Daily Scan (RSS-powered)

```bash
python relevance_scanner.py --mode daily \
    --categories cs.AI \
    --output-dir scholarx_papers/daily_$(date +%Y-%m-%d)
```

### Query-Based Search

```bash
python relevance_scanner.py --mode search \
    --query "multi-agent orchestration" \
    --categories cs.AI,cs.MA,cs.LG \
    --max-results 30 \
    --output-dir scholarx_papers/query_results
```

### Python API (Direct Library Import)

```python
from scholarx.scanner import RelevanceScanner, DEFAULT_TAXONOMY

# Daily scan
scanner = RelevanceScanner()
result = await scanner.scan_daily(
    categories=["cs.AI"],
    output_dir="scholarx_papers/daily",
)
print(f"Found {result.stats.relevant_count} relevant papers")

# Score individual papers
scored = scanner.score_papers(papers)
for sp in scored:
    if sp.score.verdict == "relevant":
        print(f"[{sp.score.total_score:.1f}] {sp.paper['title']}")
```

### MCP Tools (Agent Access)

The ScholarX MCP server exposes scanner tools:

- `scan_daily` — Full daily RSS pipeline (fetch → score → filter → download)
- `score_papers` — Search and score papers against the taxonomy

## Taxonomy

The scanner uses an 11-domain weighted keyword taxonomy:

| Domain | Weight | Description |
|--------|--------|-------------|
| `orchestration` | 3.0 | Multi-agent coordination, workflows, agentic systems |
| `knowledge_graph` | 3.0 | KG, ontology, semantic web, graph reasoning |
| `planning_reasoning` | 2.5 | CoT, ToT, MCTS, deliberation, problem solving |
| `memory_retrieval` | 2.5 | RAG, episodic memory, vector stores, long-context |
| `terminal_ui` | 2.5 | CLI, TUI, session management, workspace |
| `tool_use` | 2.0 | Function calling, MCP, code generation, plugins |
| `evaluation_safety` | 2.0 | Benchmarks, alignment, guardrails, red-teaming |
| `swarm_evolution` | 2.0 | Stigmergy, evolutionary algorithms, emergence |
| `web_ui` | 2.0 | Dashboards, visualization, graph UI, streaming |
| `llm_architecture` | 1.5 | Transformers, MoE, fine-tuning, quantization |
| `human_ai` | 1.0 | HITL, collaborative AI, dialogue systems |

### Custom Taxonomy

Supply a JSON file with `--taxonomy`:

```json
{
  "my_domain": {
    "weight": 3.0,
    "keywords": ["keyword1", "keyword2", "partial_match"]
  }
}
```

## Scoring

Papers are classified into three tiers:

- **✅ Relevant** (score ≥ 3.0) — High-value papers, PDFs downloaded automatically
- **🟡 Marginal** (score 1.0–2.9) — Potentially useful, metadata saved
- **❌ Irrelevant** (score < 1.0) — Filtered out

## Outputs

Each scan produces:

```
output_dir/
├── relevance_scores.json    # Full scoring breakdown
├── synergy_report.md        # Domain integration roadmap
├── papers_metadata.json     # Accepted paper metadata
├── paper_01.md              # Individual paper summaries
├── paper_02.md
└── pdfs/                    # Downloaded PDFs (top-scored only)
    ├── 2605.04050v1.pdf
    └── 2605.04107v1.pdf
```

## Deduplication

When `--library-dir` is specified, the scanner checks existing
`papers_metadata.json` files and skips papers already in the library.

## Integration with Comparative Analysis

The synergy report can be fed to the `comparative-analysis` skill:

```bash
# Step 1: Scan for papers
python relevance_scanner.py --mode daily --output-dir papers/daily

# Step 2: Run comparative analysis against your codebase
# (Use the comparative-analysis skill with the downloaded papers)
```

## Rate Limiting

- arXiv RSS: No explicit rate limit (updated daily at midnight EST)
- PDF downloads: 3.5s between requests (arXiv policy: 1 req/3s + margin)
- Retry: 3 attempts with exponential backoff (5s, 10s, 20s)

## Requirements

- `scholarx` package installed (`pip install -e agents/scholarx`)
- `httpx` for HTTP requests
- `pydantic` for data models
