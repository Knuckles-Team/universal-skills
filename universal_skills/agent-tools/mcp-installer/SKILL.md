---
name: mcp-installer
domain: agent-tools
skill_type: skill
description: >-
  Install a pre-configured MCP config file into various agent tool directories.
  Use when the user wants to install an mcp_config.json into Windsurf, Claude Code,
  OpenCode, Antigravity, Devin, Codex, or a custom agent path. It handles merging
  with existing configurations.
license: MIT
tags: [mcp, installer, deployment, agent-tools, config]
metadata:
  version: '1.2.1'
  author: Genius
---
# MCP Installer Skill

This skill allows you to install and merge a pre-configured `mcp_config.json` into the configuration files of various agent development tools.

## Supported Tools

- **windsurf**: `~/.codeium/windsurf/mcp_config.json`
- **claude**: `~/.claude.json` (Claude Code)
- **claude-desktop**: `~/.config/Claude/claude_desktop_config.json` (Linux XDG path)
- **opencode**: `~/.config/opencode/mcp.json`
- **antigravity**: `~/.gemini/antigravity/mcp_config.json`
- **agent-utilities** / **agent-terminal-ui**: `~/.config/agent-utilities/mcp_config.json`
- **devin**: `~/.config/devin/mcp_config.json`
- **codex**: `~/.codex/mcp_config.json`

## Tools

### install_mcp_config
Install an `mcp_config.json` file into a target tool's configuration directory. It merges the `mcpServers` object so you don't lose your existing configuration, unless you specify `--force`.

#### Arguments
- `--config`: The path to the source `mcp_config.json` file you want to install.
- `--tool`: The target tool to install into (windsurf, claude, claude-desktop, opencode, antigravity, devin, codex).
- `--path`: (Optional) Explicit custom path to the target configuration file.
- `--force`: (Optional) Overwrite existing configuration entirely rather than merging `mcpServers`.

#### Examples
```bash
# Install into Windsurf
python scripts/install.py --config ./my_mcp_config.json --tool windsurf

# Install into Antigravity (Agent Utilities XDG dir)
python scripts/install.py --config ./mcp_config.json --tool antigravity

# Install into Claude Code
python scripts/install.py --config /path/to/mcp_config.json --tool claude

# Install into a custom configuration file explicitly
python scripts/install.py --config ./mcp_config.json --path ~/.my_custom_agent/mcp.json
```
