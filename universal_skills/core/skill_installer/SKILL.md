---
name: skill-installer
description: >-
  Install and deploy universal-skills and skill-graphs into various agent tool
  directories. Use when the user wants to install skills into Windsurf, Claude
  Code, OpenCode, Antigravity, or a custom agent path. Both universal-skills and
  skill-graphs should be installed via pip first. Do NOT use for creating or
  editing skill content.
license: MIT
tags: [skills, installer, deployment, agent-tools]
metadata:
  author: Genius
  version: '0.45.0'
---
# Skill Installer Skill

This skill allows you to "install" the universal skills into the dedicated skill folders of various
agent tools — by **copy** (default) or by **symlink** (`--symlink`).

> **Prefer `--symlink`.** It links each skill to the installed `universal_skills` package instead of
> copying, so there are no duplicate files on disk and every skill auto-updates on
> `pip install -U universal-skills` (no stale copy to re-sync). It falls back to a copy if the
> filesystem refuses symlinks. This is the pattern the bundled skills already use.

## Supported Tools

OS-aware; in parity with the `mcp-installer` tool set so one bootstrap can wire both
skills and MCP config into every agent tool a host has.

- **Claude Code**: `~/.claude/skills/`
- **Claude Desktop / agent-utilities / agent-terminal-ui**: `~/.config/agent-utilities/skills/`
- **Windsurf**: `~/.codeium/windsurf/skills/`
- **OpenCode**: `~/.config/opencode/skills/`
- **OpenClaw**: `~/.openclaw/skills/`
- **Antigravity**: `~/.gemini/antigravity/skills/`
- **Codex**: `~/.codex/skills/`
- **Devin**: `~/.devin/skills/`
- **Cursor**: `~/.cursor/skills/`
- **Zed**: `~/.config/zed/skills/`

Use **`--all-detected`** to install into *every* tool present on the host in one shot
(absent tools are skipped), or `--all` for every known path.

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
- `--skills`: (Optional) Comma-separated list of skill names to install. Defaults to all.
- `--force`: (Optional) Overwrite existing skills.
- `--symlink` / `--link`: (Optional, **recommended**) Symlink skills to the installed package instead
  of copying — no duplicate files; auto-updates on `pip install -U`. Idempotent (an already-correct
  symlink is left untouched). Falls back to copy if symlinks are unavailable.
- `--install-skill-graphs`: (Optional) Also install skill-graphs from the skill-graphs repository.

```bash
# symlink all skills into Claude Code (recommended)
python install.py --tool claude --symlink

# symlink all skills into EVERY agent tool present on the host (one-command bootstrap)
python install.py --all-detected --symlink
```

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
