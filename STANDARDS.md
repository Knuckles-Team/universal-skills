# Universal Skill Standards

This document defines the mandatory structure and metadata for all skills in the `universal-skills` package. Adhering to these standards ensures consistency, discoverability, and optimal performance across all agents.

## 0. The Atomicity Edict (governing rule)

Every standard below is an application of one rule (see `AGENTS.md` for the full text):

- **Every skill is atomic** — one purpose, one trigger surface, one primary capability.
  An atomic skill's `SKILL.md` body contains **no** multi-step orchestration (no
  numbered `### Step N:` sequence, no `depends_on`). Ordered/parallel stages mean it is
  a **skill-workflow**, not a skill.
- **A skill-workflow is purely the grouping of atomic skills** — it lives in
  `universal_skills/workflows/<domain>/<name>/`, and each step references an existing
  **atomic skill** (or a single MCP tool) with `depends_on`; it adds no inline logic.
- **Skill-workflows are dual-mode** — the `depends_on` DAG (+ `references/team.yaml`)
  is the single source of truth, and the body also renders a Claude-executable
  `## Execution` section (parallel-vs-after) plus the standard graph-os delegation
  footer, so the same workflow runs under Claude OR the graph-os orchestrator.
- Enforced by `scripts/check_atomicity.py` (pre-commit/CI gate).

## 1. Directory Structure

Each skill must reside in its own directory under `universal_skills/skills/`.

```
universal_skills/skills/<skill-name>/
├── SKILL.md (required)
├── scripts/ (optional) - Executable tools/utilities
├── references/ (optional) - Documentation for agent context
└── assets/ (optional) - Templates or static resources
```

## 2. SKILL.md Requirements

### 2.1 YAML Frontmatter

Every `SKILL.md` must start with a YAML frontmatter block containing the following fields:

- `name`: (Required) Kebab-case identifier (e.g., `data-analysis`).
- `description`: (Required) Comprehensive explanation of *what* the skill does and *when* to use it.
- `categories`: (Required) A list of high-level categories. Choose from: `Core`, `Development`, `Data & Documents`, `System & Infrastructure`, `Productivity`.
- `tags`: (Optional) Descriptors for specific tools or technologies (e.g., `python`, `pdf`, `git`).
- `license`: (Optional) e.g., `MIT`.

**Example:**
```yaml
---
name: document-tools
description: "Process office documents including PDF, Excel, Word, and PowerPoint. Use when the agent needs to read, edit, or create professional document files."
categories: [Data & Documents]
tags: [pdf, excel, word, ocr]
---
```

### 2.2 Body Structure

The body of the `SKILL.md` should follow this general hierarchy:

1. **# <Skill Name>**: A level-1 heading with the human-readable name.
2. **## Overview**: A brief summary of the skill's purpose.
3. **## Workflows** (if applicable): Step-by-step guides for complex tasks.
4. **## Capabilities/Tools**: Detailed description of what the skill can do, referencing specific scripts if present.
5. **## Best Practices**: Tips for effective usage.
6. **## Resources**: Summary of bundled scripts, references, and assets.

## 3. Naming Conventions

- **Skills**: Kebab-case (e.g., `codebase-search`).
- **Scripts**: Snake_case (e.g., `list_files.py`).
- **Tools**: Clear, action-oriented names in descriptions.

## 4. Universal Guidance

- Avoid model-specific references (e.g., "Claude", "GPT"). Use "the agent".
- Always use imperative or infinitive form for instructions.
- Ensure the description is sufficient for triggering the skill without loading the body.
