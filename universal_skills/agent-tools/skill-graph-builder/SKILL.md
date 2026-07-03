---
name: skill-graph-builder
description: >-
  Transform any documentation source — a website, a PDF/Office file, a local
  directory, a single URL, a REST/DB/MCP connector, freshly generated text, or a
  Knowledge-Graph subgraph — into a polished, standardized agent skill-graph
  (SKILL.md + reference/ manual + machine-readable index.json + optional LLM-distilled
  OVERVIEW.md) with a sources.json provenance/freshness manifest, hybrid Knowledge-Graph
  + ontology enrichment, and keep-updated refresh/restyle/rebuild loops. The recipe to
  capture an entire reference manual as a reusable skill and create more.
license: MIT
tags: [skill-graph, builder, automation, docs, skill, generator, transformation]
metadata:
  author: Genius
  version: '1.0.2'
---
# Skill-Graph-Builder (Any Source → Standardized Skill-Graph)

A skill-graph is an externally-consumable corpus of knowledge packaged as an agent
skill: a `SKILL.md` index over a `reference/` markdown tree. This builder is the
**single, unified way** to create one from any source. It is a thin front-end over
the agent-utilities core pipeline
(`agent_utilities.knowledge_graph.distillation.skill_graph_pipeline`), so every
skill-graph — no matter the source — comes out in the same shape with the same
provenance + freshness tracking.

## What makes it unified

* **Any source kind** → one normalized `reference/` markdown tree:
  `web`, `pdf`, `office`, `dir`, `url_reader`, `rest`, `database`, `mcp_tool`,
  `generated` (LLM-authored), `kg_query` (distilled from the Knowledge Graph).
* **Polished, standardized output** — every graph ships:
  * a polished `SKILL.md` (badge table, a "🧭 How to use this skill-graph" agent-guidance
    block, TOC with per-folder counts) over a `reference/` markdown tree;
  * `sources.json` — provenance/freshness manifest (per source kind/uri/options,
    content-hash, fetch time + per-file integrity fingerprints);
  * `index.json` — a machine-readable navigation map (per-file path/title/group/bytes/
    headings) for programmatic jump-to;
  * optionally `OVERVIEW.md` — an **LLM-distilled essence + cheatsheet** (`--distill`),
    so the agent reads the distilled knowledge first and drills into `reference/` only
    for detail (three tiers: map → essence → full manual).
* **Content-optimized**: whitespace-normalized, exact-duplicate pages dropped (crawls
  emit the same page under many URLs) — denser signal, fewer wasted tokens.
* **Hybrid-auto KG + ontology synergy**: the offline corpus is always produced;
  when the graph daemon is reachable the corpus is **also** ingested into the
  Knowledge Graph (Document/Chunk/Concept nodes + the `SkillGraph` ontology interface),
  and the SKILL.md then tells the agent to `graph_search` the graph's domain for
  cross-cutting questions. Degrades cleanly to offline-only when the daemon is down.
* **Freshness + keep-updated**: `status` reports staleness; `refresh` re-downloads and
  re-ingests **only changed corpora** (delta); `restyle` re-renders presentation with
  no re-crawl; `rebuild` re-acquires and bumps the version.

## Create a skill-graph (CLI)

```bash
# Website (recursive crawl via this repo's crawl4ai web-crawler)
python scripts/generate_skill.py https://example.com/docs my-skill --max-depth 2

# Multiple URLs (comma-separated) — merged into one graph
python scripts/generate_skill.py "https://docs.site.com,https://api.site.com" my-skill

# A PDF (e.g. ServiceNow docs) — local path or URL
python scripts/generate_skill.py https://example.com/manual.pdf servicenow --max-file-kb 50

# A local directory of markdown / documents
python scripts/generate_skill.py ./docs my-skill --description "..."

# Distil FROM the Knowledge Graph (seed node id or natural-language query)
python scripts/generate_skill.py "" servicenow --from-kg "servicenow incident management"

# Build AND distill an OVERVIEW.md (essence + cheatsheet) in one shot
python scripts/generate_skill.py https://example.com/docs my-skill --distill

# Offline only (skip the hybrid-auto KG ingestion)
python scripts/generate_skill.py https://example.com/docs my-skill --no-kg
```

Common flags: `--max-depth`, `--max-pages`, `--max-file-kb` (split threshold),
`--disable-magic-js`, `--wait-for`, `--target-type {skills,skill-graphs}`,
`--output-dir`, `--description`, `--no-kg`, `--from-kg`, `--distill`.

> Naming: a `-docs` suffix is enforced (e.g. `my-skill` → `my-skill-docs`). The graph
> is written to the in-workspace `skill-graphs` repo when present, else a local cache,
> unless `--output-dir` is given.

## The full toolbox (the recipe to create + maintain more)

All verbs are subcommands of the core pipeline module
(`python -m agent_utilities.knowledge_graph.distillation.skill_graph_pipeline …`); the
builder CLI above is a thin front-end over `build`:

| Verb | Does |
|------|------|
| `build` | acquire any source(s) → standardized graph (+ index.json, hybrid KG) |
| `distill --dir\|--root` | LLM-distill an `OVERVIEW.md` essence/cheatsheet tier |
| `restyle --dir\|--root` | re-render SKILL.md + index.json from existing content (no re-crawl) |
| `status --dir [--quick]` | report whether a graph is stale vs its sources |
| `refresh --dir\|--root [--force]` | re-download + re-ingest **only changed** corpora (delta); cron-friendly |
| `rebuild --dir` | re-acquire from recorded sources, bump version |
| `migrate --dir\|--root [--apply]` | bring a legacy graph onto the contract (reacquire/wrap) |
| `plan --root` | classify every graph for migration |

```bash
# keep a whole library updated (delta re-ingest) — schedule via cron
python -m ...skill_graph_pipeline refresh --root /path/to/skill_graphs

# roll a presentation/renderer upgrade across every graph (cheap, offline)
python -m ...skill_graph_pipeline restyle --root /path/to/skill_graphs
```

### Crawl engine (crawl4ai) setup

`web`/`reacquire`/`refresh` re-crawl with the real JS-rendering **crawl4ai** when
available, else a basic connector. crawl4ai runs in its own interpreter so it can live
in a dedicated venv:

```bash
export SKILL_GRAPH_CRAWLER_PYTHON=/path/to/crawler-venv/bin/python  # has crawl4ai
export SKILL_GRAPH_CRAWLER=<this-repo>/research/web-crawler/scripts/crawl.py
export SKILL_GRAPH_CRAWL_TIMEOUT=900   # per-site bound; SKILL_GRAPH_MAX_PAGES caps pages
```

(See `agent-utilities/docs/guides/skill-graph-migration.md` for the full crawl4ai +
Chrome install + the migration/refresh runbook.)

## Via the Knowledge-Graph MCP surface

If graph-os is reachable, drive the same pipeline through `graph_ingest`:

* `action=build_skill_graph` — `corpus_name`=name, `target_path`=output parent dir,
  `base_path`=JSON list of sources `[{"kind","uri","options"}]` or `kind=uri,...`
  shorthand, `description`=optional.
* `action=skill_graph_status` — `target_path`=dir (`corpus_name=quick` to skip network).
* `action=rebuild_skill_graph` — `target_path`=dir.

## How it works

1. **Acquire**: each source is routed to the right extractor — this repo's crawl4ai
   web-crawler for `web`, `markitdown`/`pymupdf4llm` for documents, the agent-utilities
   source-connector registry for `rest`/`database`/`mcp_tool`/`url_reader`, an LLM for
   `generated`, and the KG distiller for `kg_query` — all normalized to markdown.
2. **Standardize**: large files are split (`mdsplit` + line fallback); a hierarchical
   TOC is built; the standardized `SKILL.md` + `sources.json` are written and validated.
3. **Enrich (hybrid-auto)**: when reachable, the corpus is ingested into the KG and
   linked to the `SkillGraph` ontology interface; a `kg_manifest.json` round-trips a
   `kg_query` graph back into another KG.
