# Universal Skill Standards

This document defines the mandatory structure and metadata for all skills in the `universal-skills` package. Adhering to these standards ensures consistency, discoverability, and optimal performance across all agents.

## 0. The Atomicity Edict (governing rule)

Every standard below is an application of one rule (see `AGENTS.md` for the full text):

- **Every skill is atomic** — one purpose, one trigger surface, one primary capability.
  An atomic skill's `SKILL.md` body contains **no** multi-step orchestration (no
  numbered `### Step N:` sequence, no `depends_on`). Ordered/parallel stages mean it is
  a **skill-workflow**, not a skill.
- **A skill-workflow is purely the grouping of atomic skills** — it lives in
  `universal_skills/<domain>-workflows/<name>/` (e.g. `finance-workflows/`,
  `infrastructure-workflows/`), and each step references an existing **atomic skill**
  (or a single MCP tool) with `depends_on`; it adds no inline logic.
- **Every SKILL.md declares a `skill_type`** — `skill` (atomic), `workflow`
  (skill-workflow), or `graph` (skill-graph). This frontmatter field — NOT the directory
  path — is how the installer (`--layer`) and the atomicity gate classify a capability,
  and it must equal the top-level `domain`'s kind. The `domain` field equals the
  containing top-level directory name.
- **Skill-workflows are dual-mode** — the `depends_on` DAG (+ `references/team.yaml`)
  is the single source of truth, and the body also renders a Claude-executable
  `## Execution` section (parallel-vs-after) plus the standard graph-os delegation
  footer, so the same workflow runs under Claude OR the graph-os orchestrator.
- Enforced by `scripts/check_atomicity.py` (pre-commit/CI gate).

## 1. Directory Structure

Each skill lives in its own directory under `universal_skills/<domain>/<skill-name>/` —
**not** `universal_skills/skills/`. `<domain>` is a top-level category directory (e.g.
`core`, `finance`, `finance-workflows`, `infrastructure`, `research-workflows`,
`system`, `web-development`) and equals the skill's `domain` frontmatter field.

```
universal_skills/<domain>/<skill-name>/
├── SKILL.md (required)
├── scripts/ (optional) - Executable tools/utilities
├── references/ (optional) - Documentation for agent context
└── assets/ (optional) - Templates or static resources
```

## 2. SKILL.md Requirements

### 2.1 YAML Frontmatter

**Required:**
- `name`: Kebab-case identifier, equal to the containing directory name (e.g. `data-analysis`).
- `description`: Comprehensive explanation of *what* the skill does and *when* to use
  it — self-sufficient without the body (agents route on the description alone).
  At most 1024 characters; no `<`/`>` (Codex rejects them in `description` — see
  §5 below).
- `skill_type`: `skill` (atomic), `workflow` (skill-workflow), or `graph`
  (skill-graph) — see the Atomicity Edict above.

**Recommended:**
- `domain`: The containing top-level directory name (e.g. `finance`, `core`).
- `metadata.version` / `metadata.author`: Version and author, as a nested mapping.
- `license`: e.g. `MIT`.

**Optional / typed** (allowed anywhere, but demoted to `metadata` on a target whose
frontmatter contract doesn't carry them — see §5):
- `tags`: Descriptors for specific tools or technologies (e.g. `python`, `pdf`, `git`).
- `requires`: Other skills/packages this skill depends on.
- `tier`: Priority/rollout tier.
- `wraps`: The upstream tool/library this skill wraps.
- `aliases`: Alternate names the skill is also known by.
- `concept`: A `CONCEPT:` id this skill traces to.

**Workflow-only** (`skill_type: workflow`):
- `agent`: The named orchestrator role driving the DAG.
- `team_config`: The swarm block (`specialist_ids`, `execution_mode`, `tool_assignments`, …).
- `depends_on`: Per-step dependency declarations (in the body's `### Step N:` DAG).
- `cron`: An optional recurring-schedule spec for autonomous runs.

**Graph-only** (`skill_type: graph`):
- `source_url`, `crawl_depth`, `built_at`, `builder_version`, `file_count`,
  `kg_ingested`, `index` — provenance/freshness fields written by
  `skill-graph-builder` (see `sources.json` / `index.json`).

`categories` is **not** a standard — drop it from new skills; it predates the
`domain`/`skill_type` taxonomy and is unused by tooling.

**Example (atomic skill):**
```yaml
---
name: document-tools
domain: core
skill_type: skill
description: >-
  Process office documents including PDF, Excel, Word, and PowerPoint. Use when the agent needs to read, edit, or create professional document files.
license: MIT
tags: [pdf, excel, word, ocr]
metadata:
  version: '1.0.0'
  author: Genius
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

## 5. Portability & the per-agent adapter

`universal-installer` is the **only** thing that emits a target agent's copy of a skill —
authors never hand-write a per-tool variant. The canonical `SKILL.md` under
`universal_skills/` stays **Claude-native** (full frontmatter, unrestricted
`description`); at install time, `universal_skills/core/universal-installer/scripts/
adapters.py` adapts a COPY for targets whose frontmatter contract is stricter.

**Per-agent allowed-top-level table.** Every target tool has an `AgentContract`
(`adapters.AGENT_CONTRACTS`):

| Target | Allowed top-level keys | Notes |
|---|---|---|
| Codex (`~/.codex/skills`) | `name`, `description`, `license`, `allowed-tools`, `metadata` | Everything else is demoted **into** `metadata` (existing `metadata` sub-keys win on conflict); `description` is sanitized (`<`→`[`, `>`→`]`); discovery is **flat** — nested sub-skills are promoted to the top level and skill-graphs install at the target's top level (not under `skill-graphs/`). (`builtin_skills`/`rename_map` are a general name-collision mechanism, currently empty — no active collision.) |
| Claude Code, Windsurf, OpenClaw, Antigravity, Devin, Cursor, Grok/Grok Code, OpenCode, Zed, agent-utilities, agent-terminal-ui | unrestricted | Permissive contract — verbatim copy/symlink, unchanged from before this adapter existed. |

A contract with every flag off (`demote_to_metadata=False`, `sanitize_description=False`,
`flat_discovery=False`, empty `rename_map`) is a no-op (`requires_transform` is False):
`install_skills()` copies/symlinks exactly as it always has. A target whose contract
`requires_transform` is **always copied, never symlinked** — the installed `SKILL.md`
diverges from the source file by construction. Run `install-skills --tool codex --path
<dir> --validate` to install and immediately check the emitted skills against the
fleet-wide frontmatter-portability gate (`scripts/check_frontmatter_portability.py`).

**The `SKILL_DIR` convention.** A skill script that needs to locate its own skill
directory (e.g. to read a bundled `references/` file, or to default an output path)
must **never** hardcode a specific agent's install root (`~/.config/devin/skills`,
`~/.codex/skills`, `~/.claude/skills`, …) — a skill is installed into a different root
per target tool. Instead:

```python
SKILL_DIR = Path(os.environ.get("SKILL_DIR") or Path(__file__).resolve().parent.parent)
```

This resolves to the skill's own directory (two levels up from `scripts/<script>.py`)
regardless of which tool it was installed into, while still letting an operator
override it explicitly via `SKILL_DIR`. Enforced (for scripts, not documentation
prose) by `scripts/check_frontmatter_portability.py`'s hardcoded-root scan.

**Windows path rules.** Every path a skill (or its scripts/skill-graphs) generates
must stay valid on Windows, macOS, and Linux:
- No trailing dot or trailing space in any path component (Windows silently drops them).
- No reserved DOS device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1`-`COM9`, `LPT1`-`LPT9`) as a bare component.
- Stay within a `MAX_PATH` budget (Windows' classic 260-char limit) — keep generated
  relative paths well under that; `skill_utilities.portable_name` / `portable_relpath`
  enforce this with a content-hash suffix on truncation so distinct inputs never collide.
- No two entries in the same directory that differ only by case (`Queues.md` vs
  `queues.md`) — collide on macOS/Windows case-insensitive filesystems;
  `skill_utilities.dedupe_caseless` resolves this.

Enforced by `scripts/check_path_portability.py` (ratchet gate, ceiling 0) and the
`skill-graph-builder`'s reference-file naming (flat, hash-named `reference/<hash>.md`
files — see its `SKILL.md`).
