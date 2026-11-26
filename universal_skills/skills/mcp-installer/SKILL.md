---
name: mcp-installer
domain: agent-tools
skill_type: skill
description: >-
  Install and merge a pre-configured MCP JSON file for Windsurf, Claude Code,
  Claude Desktop, OpenCode, Antigravity, Devin, arbora, or an explicit
  JSON target. Use when an MCP client supports the mcpServers JSON convention;
  use the client's native command instead for Codex registration.
license: MIT
tags: [mcp, installer, deployment, agent-tools, config]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
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
- **arbora** / **agent-terminal-ui**: `~/.config/arbora/mcp_config.json`
- **devin**: `~/.config/devin/mcp_config.json`

Codex is intentionally not a JSON target. Register servers through its native
`codex mcp add` command so Codex owns the corresponding `config.toml` entry. For
Arbora, meristem provides `setup-config codex`, which canonicalizes this
portable launcher without env, secrets, or machine paths:

```bash
codex mcp add arbora -- arbora --transport stdio
```

## Steps

1. Confirm the target client is a JSON target in the Supported Tools list (use `codex mcp add` for Codex) and that the source file exists with `ls ./mcp_config.json`.
   Verify that the file parses with `python3 -c "import json; json.load(open('mcp_config.json'))"`.
2. Back up the target config with `cp <target-path> <target-path>.bak` when it already exists.
   Verify that `ls <target-path>.bak` lists the backup.
3. Install with `python scripts/install.py --config ./mcp_config.json --tool <tool>` (add `--path` for a custom file, `--force` only to overwrite).
   Verify that the command exits 0 and prints the target path it wrote.
4. Check the merged result with `python3 -c "import json; print(json.load(open('<target-path>')))"`.
   Verify that both your existing servers and the newly installed ones are present.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Existing servers disappeared | `--force` replaced the whole file | Restore with `cp <target-path>.bak <target-path>` and re-run without `--force` |
| JSON decode error on the source | `mcp_config.json` is malformed | Fix the JSON syntax at the reported line, then re-run `scripts/install.py` |
| Client does not show the servers | The client was not restarted or the wrong path was used | Restart the client and pass the real config location with `--path` |
| Codex target rejected | Codex is not a JSON target | Register with `codex mcp add arbora -- arbora --transport stdio` instead |

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

# Install into Antigravity (Meristem XDG dir)
python scripts/install.py --config ./mcp_config.json --tool antigravity

# Install into Claude Code
python scripts/install.py --config /path/to/mcp_config.json --tool claude

# Install into a custom configuration file explicitly
python scripts/install.py --config ./mcp_config.json --path ~/.my_custom_agent/mcp.json
```
