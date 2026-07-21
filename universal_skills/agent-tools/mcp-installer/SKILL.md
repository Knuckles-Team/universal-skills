---
name: mcp-installer
domain: agent-tools
skill_type: skill
description: >-
  Install and merge a pre-configured MCP JSON file for Windsurf, Claude Code,
  Claude Desktop, OpenCode, Antigravity, Devin, agent-utilities, or an explicit
  JSON target. Use when an MCP client supports the mcpServers JSON convention;
  use the client's native command instead for Codex registration.
license: MIT
tags: [mcp, installer, deployment, agent-tools, config]
metadata:
  version: '1.2.1'
  author: Genius
---
# MCP Installer Skill

Use `scripts/install.py` to merge a pre-configured `mcp_config.json` into a
supported JSON-based client's configuration.

## Supported Tools

- **windsurf**: `~/.codeium/windsurf/mcp_config.json`
- **claude**: `~/.claude.json` (Claude Code)
- **claude-desktop**: `~/.config/Claude/claude_desktop_config.json` (Linux XDG path)
- **opencode**: `~/.config/opencode/mcp.json`
- **antigravity**: `~/.gemini/antigravity/mcp_config.json`
- **agent-utilities** / **agent-terminal-ui**: `~/.config/agent-utilities/mcp_config.json`
- **devin**: `~/.config/devin/mcp_config.json`

Codex is intentionally not a JSON target. Register servers through its native
`codex mcp add` command so Codex owns the corresponding `config.toml` entry. For
GraphOS, agent-utilities provides `setup-config codex`, which canonicalizes this
portable launcher without env, secrets, or machine paths:

```bash
codex mcp add graph-os -- graph-os --transport stdio
```

## Tools

### install_mcp_config
Install an `mcp_config.json` file into a target tool's configuration directory. It merges the `mcpServers` object so you don't lose your existing configuration, unless you specify `--force`.

#### Arguments
- `--config`: The path to the source `mcp_config.json` file you want to install.
- `--tool`: The JSON-config target tool (windsurf, claude, claude-desktop, opencode, antigravity, devin).
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
