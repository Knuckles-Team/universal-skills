---
name: skill-installer
domain: core
skill_type: skill
description: >-
  Install and deploy universal-skills and skill-graphs into various agent tool
  directories. Use when the user wants to install skills into Windsurf, Claude
  Code, OpenCode, Antigravity, or a custom agent path. Both universal-skills and
  skill-graphs should be installed via pip first. Do NOT use for creating or
  editing skill content.
license: MIT
tags: [skills, installer, deployment, agent-tools]
metadata:
  version: '1.1.0'
  author: Genius
---
# Skill Installer Skill

This skill allows you to "install" the universal skills into the dedicated skill folders of various
agent tools — by **copy** (default) or by **symlink** (`--symlink`).

> **Prefer `--symlink`.** It links each skill to the installed `universal_skills` package instead of
> copying, so there are no duplicate files on disk and every skill auto-updates on
> `pip install -U universal-skills` (no stale copy to re-sync). It falls back to a copy if the
> filesystem refuses symlinks. This is the pattern the bundled skills already use.

> **Refactor-safe (symlink mode).** Skills get renamed and relocated between packages over
> time. A `--symlink` install now heals stale links automatically:
> - **Repoint moved skills** — if a skill still has the same name but its **source moved** to a
>   new path (e.g. relocated from `universal-skills` into its owning agent-package), the existing
>   symlink is repointed to the new source. No `--force` needed — correcting a link to its
>   authoritative source is always safe (only a real *copied* dir still needs `--force`).
> - **Prune broken links** — a **full** install then removes any **broken** symlink (dead target)
>   left behind by a renamed or removed skill (e.g. `kg-delegation-router` → `kg-delegate` leaves a
>   dangling `kg-delegation-router` link; installing `kg-delegate` + the prune sweep resolves both).
>   Only dangling links are touched; pruning is skipped for a targeted `--skills`/`--group` run so
>   it never touches links outside its scope. Disable with `--no-prune`.

## Supported Tools

OS-aware; in parity with the `mcp-installer` tool set so one bootstrap can wire both
skills and MCP config into every agent tool a host has.

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
- **agent-utilities / agent-terminal-ui** (the canonical XDG store): `$XDG_DATA_HOME/agent-utilities/skills/`
  (default `~/.local/share/agent-utilities/skills/`; macOS `~/Library/Application Support/…`,
  Windows `%LOCALAPPDATA%\agent-utilities\skills`). This is the dir the agent-utilities agent
  factory and agent-terminal-ui **auto-load** — matching `agent_utilities.core.paths.skills_dir()`.

> **The agent-utilities XDG store is ALWAYS kept current.** Every global install writes to the
> XDG store **in addition to** whatever external tool you target — so agent-utilities itself never
> falls behind. A bare `install-skills` (no `--tool`/`--path`) updates *just* that store. Opt out
> with `--no-xdg`.

**Per-agent frontmatter adaptation (Codex).** The canonical `SKILL.md` stays
Claude-native — full frontmatter, unrestricted `description`. Codex's
`~/.codex/skills` rejects our extra top-level keys (`tags`, `categories`, `domain`,
`requires`, `tier`, `wraps`, `concept`, `team_config`, `agent`, `cron`, `skill_type`,
`aliases`, `source_url`, …) and `<`/`>` inside `description`, so installing **into
Codex** automatically:
- **Demotes** every non-Codex-recognized top-level key into a nested `metadata`
  mapping (never overwriting an existing `metadata` sub-key).
- **Sanitizes** `description` (`<`→`[`, `>`→`]`).
- **Forces a copy, never a symlink** — the emitted `SKILL.md` diverges from the
  source file, so `--symlink` is ignored for Codex (logged once).
- **Promotes nested sub-skills to the top level** — Codex has no nested discovery,
  so a genuine sub-skill bundled inside a parent skill (a nested dir with its own
  `SKILL.md`, outside `assets/`/`resources/`/`references/`/`scripts/`) installs
  alongside its parent instead of underneath it.
- **Places skill-graphs at the target's top level** (not under a `skill-graphs/`
  subfolder) — same nested-discovery reason.
- **Renames `skill-installer` → `universal-skill-installer`** — Codex reserves the
  bare `skill-installer` name for its own built-in skill of the same name.

Every other target tool (Claude Code, Windsurf, OpenClaw, Antigravity, Devin, Cursor,
Grok/Grok Code, OpenCode, Zed, agent-utilities, agent-terminal-ui) has a **permissive**
contract — verbatim copy/symlink, exactly as before this adapter existed. The
per-target contracts live in `scripts/adapters.py` (`AGENT_CONTRACTS`); see
`STANDARDS.md` §5 for the full table and the `SKILL_DIR` convention a skill's own
scripts should use instead of hardcoding an agent's install root.

Use `--validate` after installing into a transform-requiring target to immediately
run the fleet-wide frontmatter-portability gate against the emitted skills and log
any violations (a non-fatal warning; no-op outside a repo checkout):
```bash
install-skills --tool codex --path /tmp/codex-skills --force --validate
```

Use **`--all-detected`** to install into *every* tool present on the host in one shot
(absent tools are skipped), or `--all` for every known path. (Both still also update the XDG store.)

**Interactive picker (`--interactive` / `-i`).** Prefer not to guess? Run `install-skills -i`
(also auto-enabled on a bare `install-skills` when a terminal is attached). It asks two questions,
each with an **`all`** shortcut:
1. **Which detected AI tools** to install into (only tools actually present on the host).
2. **Which skill-provider packages** to install *from* — `universal-skills` **plus every
   pip-installed `agent-packages/agents/*` that ships its own skills** (each declares an
   `agent_utilities.skill_providers` entry-point; 60+ packages contribute skills this way). So
   "install everything" pulls the whole fleet's skills, not just the universal library.

Without a terminal (CI, `install.sh`), the picker is skipped and `-i` degrades to
`--all-detected` from all providers, so automation never blocks on a prompt.

## Tools

### install_skills
Copy all or specific skills from `universal-skills` to a target tool's skill directory.
Optionally install skill-graphs from the skill-graphs repository.

Both universal-skills and skill-graphs should be installed via pip first:
```bash
pip install universal-skills
pip install skill-graphs
```

#### Arguments
- `--tool`: The target tool to install into (claude, claude-desktop, windsurf, opencode, openclaw, antigravity, codex, devin, cursor, zed, agent-utilities, agent-terminal-ui, or a custom path).
- `--all-detected`: Install into every agent tool detected on this host (skips absent tools). Best for a one-command bootstrap.
- `--all`: Install into every known tool path whether or not it is detected.
- `--interactive` / `-i`: Interactively choose which **detected tools** to install into and which
  **skill-provider packages** to install from (both with an `all` option). Auto-enabled on a bare,
  TTY-attached invocation; degrades to `--all-detected` when no terminal is present.
- `--providers`: (Optional) Comma-separated skill providers to install from — `universal-skills`
  and/or agent-package names (e.g. `gitlab-api`). Defaults to every installed provider.
- `--skills`: (Optional) Comma-separated list of skill names to install. Defaults to all.
- `--force`: (Optional) Overwrite existing skills.
- `--symlink` / `--link`: (Optional, **recommended**) Symlink skills to the installed package instead
  of copying — no duplicate files; auto-updates on `pip install -U`. Idempotent (an already-correct
  symlink is left untouched). Falls back to copy if symlinks are unavailable. Symlinking also keeps
  the source repo as the single backed-up source of truth.
- `--layer`: (Optional) Which layer to install: `atomic` (atomic building-block skills only —
  **recommended for Claude**, since the agent invokes these directly), `workflows` (skill-workflows
  only — these run on the **graph-os orchestrator**; Claude fires them via the `kg-delegate`
  skill rather than holding all of them), or `all` (default).
- `--install-skill-graphs`: (Optional) Also install skill-graphs from the skill-graphs repository.
- `--no-prune`: (Optional) Do NOT remove broken symlinks left by renamed/removed skills. Pruning is
  **on by default** for a full install and is automatically skipped for a targeted
  `--skills`/`--group` run (so it only ever cleans links it's authoritative over).
- `--validate`: (Optional) After installing into a target whose contract required a
  frontmatter transform (e.g. Codex), run the frontmatter-portability gate against the
  emitted skills and log the result (a non-fatal warning on violations).

> **What to install into Claude (don't overwhelm it).** Claude loads *every* installed skill's
> `description` into context, so installing all ~430 skills bloats and dilutes skill selection.
> Recommended: symlink the **atomic layer only** into Claude (the building blocks + the
> `kg-delegate`), and leave the skill-workflows on the **graph-os orchestrator** — Claude
> discovers and fires those via `kg-delegate` / `graph_orchestrate execute_workflow` so the
> heavy DAGs run locally on graph-os, not in the Claude Code context.

```bash
# RECOMMENDED for Claude: symlink the atomic layer only (building blocks + router)
install-skills --tool claude --symlink --layer atomic

# symlink ALL skills (atomic + workflows) into Claude Code
install-skills --tool claude --symlink

# symlink the atomic layer into EVERY agent tool present on the host (one-command bootstrap)
install-skills --all-detected --symlink --layer atomic
```

> Invoke via the `install-skills` console entry point (installed with the package). Running the
> script file directly (`python install.py`) is not supported — it mis-resolves the package path.

#### Examples
```bash
# Install into a custom path explicitly
python scripts/install.py --path /path/to/my/agent/skills

# Install all skills into Windsurf
python scripts/install.py --tool windsurf

# Install specific skills into Claude Code
python scripts/install.py --tool claude --skills web-search,web-crawler

# Install into a custom path
python scripts/install.py --tool /path/to/my/agent/skills

# Install all skills and skill-graphs into OpenCode
python scripts/install.py --tool opencode --install-skill-graphs

# Install specific skills into Claude Code with skill-graphs
python scripts/install.py --tool claude --skills web-search,web-crawler --install-skill-graphs
```
