---
name: skill-graph-builder
description: Tool to transform crawled documentation into a structured agent skill. It automates the creation of a new skill directory, copies markdown files, and generates a SKILL.md with references.
categories: [Documentation, Developer Utilities]
tags: [skill-graph, builder, automation, docs, skill, generator, transformation]
---

# Skill-Graph-Builder (Docs-to-Skill Transformation)

This skill provides an automation script to turn a directory of markdown files (e.g., from a web crawl) into a fully structured agent skill (knowledge graph).

### Create a New Skill-Graph

Use `scripts/generate_skill.py` to create a new skill from a source directory of markdown files or one or more URLs.

```bash
# Single URL
python scripts/generate_skill.py https://example.com/docs my-skill --description "Description"

# Multiple URLs (comma-separated)
python scripts/generate_skill.py "https://docs.site.com,https://api.site.com" my-skill --max-depth 2
```

### Update / Rebuild a Skill-Graph

If a skill-graph was created from URL(s), the `source_url` is saved in its `SKILL.md`. You can refresh the documentation by passing the local directory as the source:

```bash
# This will find the source_url(s) in the local directory and re-crawl them
python scripts/generate_skill.py ../my-skill-docs my-skill
```

---

## How it Works

1.  **Crawl**: If a URL is provided (or found in an existing skill), it uses the `web-crawler` skill to recursively download markdown content.
2.  **Transform**: It organizes the content into a `reference/` directory.
3.  **Index**: It generates a structured `SKILL.md` with links to all captured documents and tracks the `source_url` for future updates.
4.  **SKILL.md Generation**: Generates a `SKILL.md` in the new skill directory that lists all documentation files as clickable links with their titles extracted from the content.

## Example

If you crawled `https://ai.pydantic.dev` to `Workspace/agent-packages/docs/pydantic-ai`:

```bash
python scripts/generate_skill.py ~/.cache/universal-skills/skill-graphs/pydantic-ai pydantic-ai-docs --description "Agent skill for Pydantic AI framework documentation."
```
