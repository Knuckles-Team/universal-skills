# Universal Skill Standards

This document defines the mandatory structure and metadata for all skills in the `universal-skills` package. Adhering to these standards ensures consistency, discoverability, and optimal performance across all agents.

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
