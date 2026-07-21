#!/usr/bin/env python3
"""Portable graph-os + fleet MCP wiring for JSON-config clients.

Builds the ``mcpServers`` entries this skill is responsible for (graph-os +
auto-detected ``agents/*`` servers) and merges them into a target agent tool's
MCP config file by importing ``mcp-installer``'s own merge machinery — this
module never re-implements config-file reading/writing/merging/backup.

Grounding for the entry shapes (no invented fields):
- Every ``agents/*`` README's ``mcp_config.json`` example publishes the same
  stdio shape: ``{"command": "uvx", "args": ["--from", "<pkg>[mcp]",
  "<console-script>"], "env": {"MCP_TOOL_MODE": ..., ...}}`` (e.g.
  ``agents/gitlab-api/README.md``, ``agents/servicenow-api/README.md``,
  ``agents/github-agent/README.md``), and the remote/Streamable-HTTP
  alternative is a bare ``{"url": "<url>"}`` (same READMEs, "Alternatively,
  connect to a pre-deployed Streamable-HTTP instance by `url`").
- The graph-os launcher is the installed, machine-neutral console script with
  explicit stdio transport. Deployment topology and runtime state resolve from
  AgentConfig rather than being copied into a client registration.
- The per-package MCP console-script name is **never guessed** (it is not a
  fixed suffix transform — ``gitlab-api`` → ``gitlab-mcp``, ``github-agent`` →
  ``github-mcp``, i.e. package-specific) — it is read from real
  ``console_scripts`` entry-point metadata (pip-installed) or the package's own
  ``[project.scripts]`` table (``--from-package``), never fabricated.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from agent_utilities.base_utilities import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
else:
    logger = get_logger(__name__)

# Load mcp-installer's own install.py by file path (same technique install.py
# already uses for adapters.py) — it is dev-only tooling bundled as a sibling
# skill, not a separate pip package, so there is no dotted import path.
_MCP_INSTALLER_SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "agent-tools"
    / "mcp-installer"
    / "scripts"
    / "install.py"
)


def _load_mcp_installer():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "universal_skills._mcp_installer_impl", _MCP_INSTALLER_SCRIPT
    )
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mcp_installer = _load_mcp_installer() if _MCP_INSTALLER_SCRIPT.is_file() else None

# MCP-config destination paths, in parity with install.py's skill-directory
# TOOL_PATHS. Extends mcp-installer's own (pre-existing) set with Cursor —
# required by this skill's target-tool list but previously only supported on
# the skill-directory leg, not the MCP-config leg. Grounded via the vendored
# fastmcp docs skill-graph (`~/.cursor/mcp.json`, all platforms).
if _mcp_installer is not None:
    MCP_CONFIG_PATHS: Dict[str, Path] = dict(_mcp_installer.TOOL_PATHS)
    MCP_CONFIG_PATHS.setdefault("cursor", Path("~/.cursor/mcp.json").expanduser())
else:  # pragma: no cover - only when mcp-installer skill is missing entirely
    MCP_CONFIG_PATHS = {}


def detect_present_mcp_tools() -> Dict[str, Path]:
    present = (
        dict(_mcp_installer.detect_present_tools()) if _mcp_installer is not None else {}
    )
    cursor_cfg = MCP_CONFIG_PATHS.get("cursor")
    if cursor_cfg is not None and cursor_cfg.parent.exists():
        present.setdefault("cursor", cursor_cfg)
    return present


def build_graph_os_entry(
    mode: str = "stdio",
    remote_url: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Build the ``graph-os`` mcpServers entry for ``mode`` (stdio|remote|skip)."""
    if mode == "skip":
        return None
    if mode == "remote":
        if not remote_url:
            logger.error("--graph-os remote requires --graph-os-url.")
            return None
        return {"url": remote_url}
    return {"command": "graph-os", "args": ["--transport", "stdio"]}


def _dist_mcp_console_scripts(dist_name: str) -> List[str]:
    """Real ``console_scripts`` entry-point names ending ``-mcp`` for a pip-installed
    distribution — never guessed from the package name."""
    from importlib.metadata import distribution

    try:
        dist = distribution(dist_name)
    except Exception:  # noqa: BLE001 - not installed under this exact name
        return []
    names: List[str] = []
    for ep in dist.entry_points:
        if ep.group == "console_scripts" and ep.name.endswith("-mcp"):
            names.append(ep.name)
    return sorted(set(names))


def build_agent_server_entries(
    provider_names: List[str],
    tool_mode: str = "condensed",
    from_package_scripts: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Dict[str, Any]]:
    """One ``uvx --from <pkg>[mcp] <console-script>`` entry per real MCP script.

    ``provider_names`` are pip-installed distribution names (resolved via real
    ``console_scripts`` metadata). ``from_package_scripts`` (optional) maps a
    package name installed via ``--from-package`` to the ``*-mcp`` script names
    read directly from its ``pyproject.toml`` ``[project.scripts]`` table —
    same shape, sourced from source instead of installed metadata.
    """
    entries: Dict[str, Dict[str, Any]] = {}
    for pkg in provider_names:
        for script in _dist_mcp_console_scripts(pkg):
            entries[script] = {
                "command": "uvx",
                "args": ["--from", f"{pkg}[mcp]", script],
                "env": {"MCP_TOOL_MODE": tool_mode},
            }
    for pkg, scripts in (from_package_scripts or {}).items():
        for script in scripts:
            entries[script] = {
                "command": "uvx",
                "args": ["--from", f"{pkg}[mcp]", script],
                "env": {"MCP_TOOL_MODE": tool_mode},
            }
    return entries


def merge_and_write(target_path: Path, servers: Dict[str, Dict[str, Any]]) -> bool:
    """Merge ``servers`` into ``target_path``'s ``mcpServers``, via mcp-installer."""
    if _mcp_installer is None:
        logger.warning(
            "mcp-installer skill not found alongside universal-installer; "
            "skipping MCP config wiring for %s.",
            target_path,
        )
        return False
    if not servers:
        return True
    source_data = {"mcpServers": servers}
    if not target_path.exists():
        return bool(_mcp_installer.save_json(target_path, source_data))
    backup_path = target_path.with_suffix(".json.bak")
    try:
        shutil.copy2(target_path, backup_path)
    except Exception as e:  # noqa: BLE001
        logger.warning("Failed to back up %s: %s", target_path, e)
    target_data = _mcp_installer.load_json(target_path)
    merged = _mcp_installer.merge_mcp_configs(source_data, target_data)
    return bool(_mcp_installer.save_json(target_path, merged))


def wire_mcp_config(
    tool_key: str,
    target_path: Optional[Path],
    graph_os_mode: str,
    graph_os_url: Optional[str],
    provider_names: List[str],
    from_package_scripts: Optional[Dict[str, List[str]]] = None,
    tool_mode: str = "condensed",
) -> bool:
    """Build + merge the graph-os and fleet-server entries for one target tool."""
    dest = target_path or MCP_CONFIG_PATHS.get(tool_key.lower())
    if dest is None:
        logger.info(
            "No MCP config path known for tool '%s'; skipping MCP wiring.", tool_key
        )
        return False
    servers: Dict[str, Dict[str, Any]] = {}
    graph_os_entry = build_graph_os_entry(graph_os_mode, graph_os_url)
    if graph_os_entry is not None:
        servers["graph-os"] = graph_os_entry
    servers.update(
        build_agent_server_entries(provider_names, tool_mode, from_package_scripts)
    )
    if not servers:
        return True
    logger.info(f"→ MCP config for {tool_key}: {dest} ({len(servers)} server(s))")
    return merge_and_write(dest, servers)
