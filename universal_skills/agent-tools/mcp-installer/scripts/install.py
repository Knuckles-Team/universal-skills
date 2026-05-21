#!/usr/bin/env python3
import argparse
import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def get_tool_paths() -> Dict[str, Path]:
    """Return tool paths dynamically based on the OS."""
    is_windows = sys.platform == "win32"
    is_mac = sys.platform == "darwin"

    appdata = (
        Path(os.environ.get("APPDATA", "~\\AppData\\Roaming")).expanduser()
        if is_windows
        else None
    )

    paths = {
        "windsurf": Path("~/.codeium/windsurf/mcp_config.json").expanduser(),
        "claude": Path("~/.claude.json").expanduser(),
        "antigravity": Path("~/.gemini/antigravity/mcp_config.json").expanduser(),
        "devin": Path("~/.devin/mcp_config.json").expanduser(),
        "codex": Path("~/.codex/mcp_config.json").expanduser(),
    }

    # Claude Desktop
    if is_windows:
        paths["claude-desktop"] = appdata / "Claude" / "claude_desktop_config.json"
    elif is_mac:
        paths["claude-desktop"] = Path(
            "~/Library/Application Support/Claude/claude_desktop_config.json"
        ).expanduser()
    else:
        paths["claude-desktop"] = Path(
            "~/.config/Claude/claude_desktop_config.json"
        ).expanduser()

    # OpenCode
    if is_windows:
        paths["opencode"] = appdata / "opencode" / "mcp.json"
    else:
        paths["opencode"] = Path("~/.config/opencode/mcp.json").expanduser()

    # Agent Utilities / Agent Terminal UI
    if is_windows:
        localappdata = Path(
            os.environ.get("LOCALAPPDATA", "~\\AppData\\Local")
        ).expanduser()
        agent_utils_path = localappdata / "agent-utilities" / "mcp_config.json"
    elif is_mac:
        agent_utils_path = Path(
            "~/Library/Application Support/agent-utilities/mcp_config.json"
        ).expanduser()
    else:
        agent_utils_path = Path(
            "~/.config/agent-utilities/mcp_config.json"
        ).expanduser()

    paths["agent-utilities"] = agent_utils_path
    paths["agent-terminal-ui"] = agent_utils_path

    return paths


TOOL_PATHS = get_tool_paths()


def load_json(filepath: Path) -> Dict[str, Any]:
    """Load a JSON file, returning an empty dict if it doesn't exist or is empty."""
    if not filepath.exists():
        return {}
    try:
        content = filepath.read_text(encoding="utf-8").strip()
        if not content:
            return {}
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from {filepath}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return {}


def save_json(filepath: Path, data: Dict[str, Any]) -> bool:
    """Save data to a JSON file, creating parent directories if needed."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return True
    except Exception as e:
        logger.error(f"Error writing to {filepath}: {e}")
        return False


def merge_mcp_configs(
    source_data: Dict[str, Any], target_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Merge two MCP configuration dictionaries."""
    merged = target_data.copy()

    # Ensure mcpServers exists in merged data
    if "mcpServers" not in merged or not isinstance(merged["mcpServers"], dict):
        merged["mcpServers"] = {}

    source_servers = source_data.get("mcpServers", {})
    if not isinstance(source_servers, dict):
        logger.warning(
            "Source configuration does not have a valid 'mcpServers' object."
        )
        return merged

    for server_name, server_config in source_servers.items():
        if server_name in merged["mcpServers"]:
            logger.info(f"Updating existing server configuration for '{server_name}'")
        else:
            logger.info(f"Adding new server configuration for '{server_name}'")
        merged["mcpServers"][server_name] = server_config

    return merged


def install_mcp_config(
    source_path: Path, target_path: Path, force: bool = False
) -> bool:
    """Install the MCP configuration into the target path."""
    if not source_path.exists():
        logger.error(f"Source configuration file not found: {source_path}")
        return False

    source_data = load_json(source_path)
    if not source_data:
        logger.error("Source configuration is empty or invalid.")
        return False

    if not target_path.exists() or force:
        logger.info(f"Writing configuration directly to {target_path}...")
        return save_json(target_path, source_data)

    # Merge configurations
    logger.info(f"Merging configuration with existing file at {target_path}...")

    # Create backup before merging
    backup_path = target_path.with_suffix(".json.bak")
    try:
        shutil.copy2(target_path, backup_path)
        logger.info(f"Created backup at {backup_path}")
    except Exception as e:
        logger.warning(f"Failed to create backup: {e}")

    target_data = load_json(target_path)
    merged_data = merge_mcp_configs(source_data, target_data)

    return save_json(target_path, merged_data)


def main():
    parser = argparse.ArgumentParser(
        description="Install an MCP configuration file into agent tools"
    )
    parser.add_argument(
        "--config", required=True, help="Path to the source mcp_config.json file"
    )
    parser.add_argument(
        "--tool",
        choices=list(TOOL_PATHS.keys()),
        help="Target tool (windsurf, claude, claude-desktop, opencode, antigravity, devin, codex)",
    )
    parser.add_argument(
        "--path", help="Explicit custom path to the target configuration file"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing configuration instead of merging",
    )

    args = parser.parse_args()

    if args.path:
        target = Path(args.path).expanduser()
    elif args.tool:
        target = TOOL_PATHS[args.tool.lower()]
    else:
        logger.error("Either --tool or --path must be specified.")
        sys.exit(1)

    source = Path(args.config).expanduser()

    success = install_mcp_config(source, target, args.force)
    if success:
        logger.info(f"Successfully installed MCP configuration to {target}")
    else:
        logger.error("Failed to install MCP configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()
