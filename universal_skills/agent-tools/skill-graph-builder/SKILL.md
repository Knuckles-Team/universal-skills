---
name: skill-graph-builder
description: >-
  Transform any documentation source — a website, a PDF/Office file, a local
  directory, a single URL, a REST/DB/MCP connector, freshly generated text, or a
  Knowledge-Graph subgraph — into a standardized agent skill-graph (SKILL.md +
  reference/ tree) with a sources.json provenance/freshness manifest, optional
  Knowledge-Graph + ontology enrichment, and a staleness/rebuild loop. Use to
  capture and pass on a corpus of knowledge as a reusable skill.
license: MIT
tags: [skill-graph, builder, automation, docs, skill, generator, transformation]
metadata:
  author: Genius
  version: '0.45.0'
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
* **Standardized output**: a `SKILL.md` with a consistent frontmatter superset
  (`skill_graph_version`, `source_types`, `built_at`, `builder_version`,
  `file_count`, `kg_ingested`, `concepts`, …) and a `sources.json` provenance
  manifest recording, per source, the kind/uri/options, content-hash and fetch time,
  plus a per-file integrity fingerprint.
* **Hybrid-auto KG + ontology synergy**: the offline corpus is always produced;
  when the graph daemon is reachable the corpus is **also** ingested into the
  Knowledge Graph (Document/Chunk/Concept nodes, the `SkillGraph` ontology
  interface), so the KG can reason about which graphs cover which concepts. It
  degrades cleanly to offline-only when the daemon is down.
* **Freshness + rebuild**: `status` reports whether a graph is stale vs its sources;
  `rebuild` re-acquires and bumps the version.

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

# Offline only (skip the hybrid-auto KG ingestion)
python scripts/generate_skill.py https://example.com/docs my-skill --no-kg
```

Common flags: `--max-depth`, `--max-pages`, `--max-file-kb` (split threshold),
`--disable-magic-js`, `--wait-for`, `--target-type {skills,skill-graphs}`,
`--output-dir`, `--description`, `--no-kg`, `--from-kg`.

> Naming: a `-docs` suffix is enforced (e.g. `my-skill` → `my-skill-docs`). The graph
> is written to the in-workspace `skill-graphs` repo when present, else a local cache,
> unless `--output-dir` is given.

## Check freshness / rebuild

These run via the core pipeline (any agent with graph-os can also call them through
`graph_ingest`):

```bash
# Is the graph stale relative to its sources? (--quick skips network sources)
python -m agent_utilities.knowledge_graph.distillation.skill_graph_pipeline \
    status --dir /path/to/skill-graph --quick

# Re-acquire from the recorded sources and bump the version
python -m agent_utilities.knowledge_graph.distillation.skill_graph_pipeline \
    rebuild --dir /path/to/skill-graph
```

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
