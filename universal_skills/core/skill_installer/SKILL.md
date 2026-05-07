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
  version: '0.8.0'
---
# Skill Installer Skill

This skill allows you to "install" the universal skills by copying them into the dedicated skill folders of various agent tools.

## Supported Tools

- **Windsurf**: `~/.codeium/windsurf/skills/`
- **Claude Code**: `~/.claude/skills/`
- **OpenClaw**: `~/.openclaw/skills/`
- **OpenCode**: `~/.config/opencode/skills/`
- **Antigravity**: `~/.agents/skills/`

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
- `--tool`: The target tool to install into (windsurf, claude, openclaw, opencode, antigravity, or a custom path).
- `--skills`: (Optional) Comma-separated list of skill names to install. Defaults to all.
- `--force`: (Optional) Overwrite existing skills.
- `--install-skill-graphs`: (Optional) Also install skill-graphs from the skill-graphs repository.

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
