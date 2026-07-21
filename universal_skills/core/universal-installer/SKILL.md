---
name: universal-installer
domain: core
skill_type: skill
description: >-
  Install and wire the whole fleet contribution surface into an agent tool in one
  step: skills, skill-graphs, skill-workflows, ontologies, and system prompts —
  plus generating/patching supported JSON-client MCP configuration to wire
  graph-os (portable local stdio, or a remote instance) and auto-detected agents/* MCP
  server. Supports installing from pip-installed providers or directly from an
  agents/* project checkout. Use when the user wants to install skills or
  ontologies or prompts into Windsurf, Claude Code, OpenCode, Antigravity,
  Codex, Devin, Cursor, or a custom agent path, or wants an agent tool wired up
  end-to-end (skills + MCP servers) in one command. Do NOT use for creating or
  editing skill/ontology/prompt content — use skill-builder /
  skill-workflow-builder / skill-graph-builder for that.
license: MIT
tags: [skills, ontologies, prompts, mcp, installer, deployment, agent-tools]
metadata:
  version: '1.2.1'
  author: Genius
  supersedes: skill-installer
---
# Universal Installer Skill

The successor to `skill-installer`. Installs the **whole fleet contribution surface**
into agent-tool directories by **copy** (default) or **symlink** (`--symlink`), in
one entry point per artifact type:

- **Skills, skill-graphs, skill-workflows** — into each target tool's skill directory
  (unchanged behavior from `skill-installer`; every capability below is additive).
- **Ontologies + system prompts** — the other two legs of the
  `agent_utilities.*_providers` entry-point federation (CONCEPT:AU-KG.ontology.federation-provider-leg /
  CONCEPT:AU-OS.deployment.modular-skill-prompt-contribution), materialized into the canonical
  agent-utilities XDG tree (`$XDG_DATA_HOME/agent-utilities/{prompts,ontologies}/<provider>/…`)
  so the KG/epistemic-graph side can ingest them — see "Ontology & prompt
  installation" below.
- **graph-os + fleet MCP wiring** — generates/patches supported JSON clients
  with a portable installed `graph-os` stdio entry (or a remote URL), plus one
  entry per auto-detected `agents/*` MCP server — see
  "MCP server wiring" below.
- **Per-package auto-detection**, including installing directly from an
  `agents/*` project checkout that isn't pip-installed yet (`--from-package`).

> **Prefer `--symlink`** for skills/skill-graphs (unchanged from `skill-installer`):
> links each skill to the installed package instead of copying, so there are no
> duplicate files on disk and every skill auto-updates on `pip install -U`.
> Ontologies and prompts are always **copied** (they are consumed as data by
> agent-utilities/epistemic-graph, not executed in place).

> **Refactor-safe (symlink mode).** A `--symlink` install repoints a moved skill's
> stale link to its new source and prunes broken links left by a renamed/removed
> skill on a full install (`--no-prune` to disable) — unchanged from `skill-installer`.

## Supported Tools

OS-aware; kept in parity across the skill-directory leg and the MCP-config leg so one
bootstrap wires both.

**Skill/skill-graph directories** (`--tool`):
- **Claude Code**: `~/.claude/skills/`
- **Windsurf**: `~/.codeium/windsurf/skills/`
- **OpenCode**: `~/.config/opencode/skills/`
- **OpenClaw**: `~/.openclaw/skills/`
- **Antigravity**: `~/.gemini/antigravity/skills/`
- **Codex**: `~/.codex/skills/`
- **Devin**: `~/.config/devin/skills/`
- **Cursor**: `~/.cursor/skills/`
- **Grok Code** (`grok` / `grok-code`): `~/.grok/skills/`
- **Zed**: `~/.config/zed/skills/`
- **agent-utilities / agent-terminal-ui** (canonical XDG store): `$XDG_DATA_HOME/agent-utilities/skills/`
  — always kept current on every global install (opt out with `--no-xdg`).

**MCP config files** (same `--tool` key, MCP-config leg): Claude Code (`~/.claude.json`),
Claude Desktop, Windsurf, OpenCode, Antigravity, Devin, Codex, Cursor
(`~/.cursor/mcp.json`), and agent-utilities/agent-terminal-ui — the full set the bundled
`mcp-installer` supports (extended with **Cursor**, previously skill-only-parity).
`merge`, never overwrite, unless `--force`.

**Per-agent frontmatter adaptation (Codex)** — unchanged from `skill-installer`:
canonical `SKILL.md` stays Claude-native; installing into Codex's flat-discovery,
restricted-frontmatter `~/.codex/skills` demotes non-Codex keys into `metadata`,
sanitizes `description`, forces a copy (never symlink), and promotes nested
sub-skills + skill-graphs to the target's top level. Full contract table in
`STANDARDS.md` §5. (The old `skill-installer` → `universal-skill-installer`
Codex name-collision rename is gone — the skill itself is no longer named
`skill-installer`, so the collision with Codex's own built-in no longer applies.)

## Tools

### install_skills (skills / skill-graphs / skill-workflows)

Unchanged interface from `skill-installer` — see full flag reference below. Both
`universal-skills` and `skill-graphs` should be pip-installed first:
```bash
pip install universal-skills
pip install skill-graphs
```

#### Arguments
- `--tool`: Target tool (claude, claude-desktop, windsurf, opencode, openclaw,
  antigravity, codex, devin, cursor, grok, zed, agent-utilities,
  agent-terminal-ui, or a custom path).
- `--all-detected` / `--all`: Install into every detected / every known tool.
- `--interactive` / `-i`: Interactively pick target tools, source providers, AND
  the graph-os MCP wiring mode (new — see below). Auto-enabled on a bare
  TTY-attached invocation.
- `--providers`: Comma-separated skill/prompt/ontology providers to install from
  (`universal-skills` and/or installed agent-package names). Default: all.
- `--from-package <path>`: Install directly from an `agents/*` project checkout
  that is **not yet pip-installed** — parses its `pyproject.toml`
  `agent_utilities.{skill,prompt,ontology}_providers` entry-points and installs
  straight from the checkout's source tree. See "Per-package auto-detection".
- `--skills`, `--group`, `--force`, `--symlink`/`--link`, `--layer`,
  `--install-skill-graphs`, `--no-prune`, `--no-xdg`, `--validate`: unchanged
  from `skill-installer` (see below for the full description of each).
- `--no-ontologies` / `--no-prompts`: Skip the ontology / prompt install leg
  (both run by default — see below).
- `--graph-os {stdio,remote,skip}`: How to wire graph-os into the target's MCP
  config (default `stdio`; interactive picker asks if not given and a TTY is
  attached). See "MCP server wiring".
- `--graph-os-url <url>`: Remote graph-os URL, required when `--graph-os remote`.
- `--no-mcp`: Skip MCP config wiring entirely (skills/ontologies/prompts only).

```bash
# RECOMMENDED for Claude: symlink the atomic layer, wire graph-os + fleet MCP servers
install-universal --tool claude --symlink --layer atomic --graph-os stdio

# Install everything into every detected tool (interactive picker if TTY-attached)
install-universal --all-detected --symlink

# Wire a remote graph-os instead of the installed local stdio launcher
install-universal --tool claude --graph-os remote --graph-os-url https://graph-os.example.com/mcp

# Install directly from an unreleased agents/* checkout (skills+prompts+ontology)
install-universal --tool claude --from-package ${AGENT_UTILITIES_WORKSPACE_ROOT}/agent-packages/agents/gitlab-api
```

> Invoke via the `install-universal` console entry point (installed with the
> package). The legacy `install-skills` console entry (from `skill-installer`)
> still works and now points at this same implementation — no functionality lost.

## Ontology & prompt installation (new)

agent-utilities already defines the full three-leg federation — `agent_utilities.
skill_providers` / `.prompt_providers` / `.ontology_providers` entry-points,
resolved by `agent_utilities.core.providers` and materialized by
`agent_utilities.core.unified_install.install_unified()` into
`$XDG_DATA_HOME/agent-utilities/{skills,prompts,ontologies}/<provider>/…`. This
skill's job on the ontology/prompt legs is to make sure that materialization
happens as part of the SAME install run a user already runs for skills, without
requiring a separate `agent-utilities install` invocation:

- If `agent_utilities` is importable, `install_unified()` is called directly
  (best fidelity — reuses AU's own federation-aware logic, including AU's own
  base ontologies/prompts).
- Otherwise (agent-utilities not installed in this environment), a local,
  dependency-free fallback in `scripts/providers.py` resolves the same
  `agent_utilities.prompt_providers` / `agent_utilities.ontology_providers`
  entry-points and copies each provider's `*.json` prompts / `*.ttl` (+
  `shapes/*.ttl`) ontology files into the same XDG layout directly — same
  target tree, no agent-utilities import required (mirrors the existing
  skill-provider fallback pattern already used for skills).

Ontologies/prompts always land in the XDG tree (never in a per-tool skill
directory — Claude Code etc. don't consume `.ttl`/prompt JSON directly); only
the skills/skill-graphs leg is tool-specific. Skip with `--no-ontologies` /
`--no-prompts`.

## Per-package auto-detection (new)

When an `agents/*` package is **already pip-installed**, its skills/prompts/
ontologies are picked up automatically through the standard entry-point
discovery above — nothing new to invoke.

When it is **not yet installed** (a checkout you're developing against, e.g.
`agent-packages/agents/<pkg>`), pass `--from-package <path>`:
`scripts/from_package.py` reads that package's `pyproject.toml` directly
(stdlib `tomllib`, no network/pip needed) for its
`[project.entry-points."agent_utilities.skill_providers"]` /
`.prompt_providers` / `.ontology_providers` tables, resolves each value
(`<module>.skills` etc.) to a source directory inside the checkout, and installs
from there through the same skill/ontology/prompt install paths as a normal
provider — named by the package's `[project].name`.

## MCP server wiring (new)

Reuses the bundled **`mcp-installer`** skill's config-merge machinery
(`merge_mcp_configs` / `install_mcp_config` — never overwrites unrelated
`mcpServers` entries, backs up the target file before merging) rather than
re-implementing it. `scripts/mcp_setup.py` builds two kinds of entries and
merges them into a supported JSON client's MCP config file. Codex remains a
skill-install target, but is intentionally skipped by this JSON leg. Register
GraphOS in Codex through agent-utilities' `setup-config codex` command (or the
equivalent `codex mcp add graph-os -- graph-os --transport stdio`) so Codex owns
its `config.toml` entry and no env, secret, working directory, or machine path
is copied.

1. **`graph-os`**:
   - `--graph-os stdio` (default): wires the installed portable launcher as
     `"command": "graph-os", "args": ["--transport", "stdio"]`. Runtime
     topology and state resolve through AgentConfig, not client env fields.
   - `--graph-os remote --graph-os-url <url>`: wires `{"url": "<url>"}` — the
     Streamable-HTTP/remote shape every `agents/*` README documents as the
     alternative to stdio.
   - `--graph-os skip`: no graph-os entry is written.
2. **Auto-detected `agents/*` servers** — for every provider discovered on this
   install run (pip-installed or `--from-package`) that also declares an
   `[project.scripts]` `*-mcp` entry point, adds
   `"command": "uvx", "args": ["--from", "<pkg>[mcp]", "<pkg>-mcp"], "env":
   {"MCP_TOOL_MODE": "condensed"}` — the universal shape. Per-package tool
   toggles (`<X>TOOL`) and auth env vars are package-specific and are **not**
   guessed; the merged entry is a ready-to-fill-in starting point, matching
   what that package's own README documents.

**Interactive decision point.** `--interactive`/bare-TTY invocation asks,
per the picker in `install.py`'s `_run_interactive()`: *"Wire graph-os as (1)
local stdio (installed console script), (2) a remote instance (enter URL), or (3)
skip?"* — mirrors the tool/provider pickers already there. Non-interactively,
`--graph-os` defaults to `stdio` (never silently skipped, since a graph-os
entry is the common case) unless `--no-mcp` is given.

## Ontology / skill / prompt auto-extension hook for the KG (new, partial)

After each install run (fleet-provider or `--from-package`), the installer
writes a small JSON manifest —
`$XDG_DATA_HOME/agent-utilities/install-manifest.json` — recording, per
provider, which artifact types and how many were (re)installed this run and
when. This is the "make the artifacts **discoverable**" half of KG
auto-extension: any provider whose skills/prompts/ontologies changed is now
sitting in the canonical XDG tree the KG ingestion pipeline already scans.

**What this skill does NOT do** (by design — this is the graph-os/epistemic-graph
side's job, not the installer's): actually parse the manifest, mint KG nodes, or
call `source_sync`. The installer prints the exact follow-up
(`source_sync source=all mode=delta` via the graph-os MCP connection, or the
`agent-utilities-source-integration` skill) rather than invoking it itself —
invoking a heavy KG-ingestion tool from inside a lightweight file-copy installer
would couple the two concerns and require a live graph-os connection this skill
has no business assuming. If a graph-os-side counterpart wants to consume
`install-manifest.json` directly (rather than re-scanning the whole XDG tree),
that consumer is **not yet built** — flagged as a deferred follow-up.

## Best Practices

- Prefer `--symlink` for the skill/skill-graph leg on any host you'll keep
  `pip install -U`-ing.
- Run with `--interactive` (or bare, TTY-attached) the first time on a new host —
  it walks tools, providers, AND the graph-os wiring decision in one pass.
- Use `--from-package` while developing a new `agents/*` connector, before it's
  released to pip — no need to `pip install -e` first.
- After any run that changed provider content, follow the printed `source_sync`
  hint so the KG picks up the new/changed skills, prompts, and ontology.

## Resources
- `scripts/install.py` — skill/skill-graph install core (unchanged logic from
  `skill-installer`) + the new `--from-package`/`--graph-os`/ontology-prompt CLI
  wiring.
- `scripts/adapters.py` — per-agent-tool `SKILL.md` frontmatter contracts
  (unchanged).
- `scripts/providers.py` — ontology/prompt entry-point discovery + XDG
  materialization (agent-utilities-import fast path + dependency-free fallback).
- `scripts/from_package.py` — parse an `agents/*` checkout's `pyproject.toml`
  entry-points and install directly from source.
- `scripts/mcp_setup.py` — graph-os + fleet MCP config generation, merged via
  the bundled `mcp-installer`.
