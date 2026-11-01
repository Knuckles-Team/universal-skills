---
name: skill-graph-builder
domain: agent-tools
skill_type: skill
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
  version: '1.5.2'
  author: Genius
---
# Skill-Graph-Builder (Any Source → Standardized Skill-Graph)

A skill-graph is an externally-consumable corpus of knowledge packaged as an agent
skill: a `SKILL.md` index over a `reference/` markdown tree. This builder is the
**single, unified way** to create one from any source. It is a thin front-end over
the local `scripts/_pipeline.py`, so every skill-graph — no matter the source —
comes out in the same shape with the same provenance tracking.

## What it produces

* **Source kinds**: `web` (the repo's crawl4ai web-crawler), `pdf` and `office`
  (local path or URL; needs `pymupdf4llm` / `markitdown`), `dir` (markdown and text
  files) and `kg_query` (read through the served arbora search twin; set `ARBORA_URL`).
* **Standardized output** for every graph: `SKILL.md` (`skill_type: graph`) with a table
  of contents, `sources.json` (schema `skill-graph-sources/v1`, per-file sha256),
  `index.json` (per-section path, title, group, url) and a flat `reference/<hash>.md`
  tree. Large files split at `--max-file-kb`.
* **`--distill`** writes an extractive `OVERVIEW.md` (section leads), with no LLM call.

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

```

Common flags: `--max-depth`, `--max-pages`, `--max-file-kb` (split threshold),
`--disable-magic-js`, `--wait-for`, `--target-type {skills,skill-graphs}`,
`--output-dir`, `--description`, `--from-kg`, `--distill`.

> Naming: a `-docs` suffix is enforced (e.g. `my-skill` → `my-skill-docs`). The graph
> is written to the in-workspace `skill-graphs` repo when present, else a local cache,
> unless `--output-dir` is given.

## How it works

`scripts/generate_skill.py` classifies the sources and calls `scripts/_pipeline.py`,
which acquires documents, splits them, and writes the layout above. The script then
flattens `reference/` to hashed names and repoints `index.json`, `sources.json` and the
`SKILL.md` links. The pipeline imports no engine or agent-runtime package.

## Moving to medulla

The `refresh`, `restyle`, `status`, `rebuild` and `migrate` verbs and the KG ingestion
of the corpus belonged to the retired agent-utilities pipeline. Native distillation
moves to `MEDULLA-TYPED-PACKS-R700.7` and is served through arbora. Medulla validates
and imports the finished bundle (`MEDULLA-TYPED-PACKS-R700`). Rebuild a graph by
running the CLI again. The builder writes the offline corpus only; the flags `--no-kg`,
`--ingest-kg` and `--append` are removed.
