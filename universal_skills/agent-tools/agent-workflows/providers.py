"""
Provider configuration system for agent-manager.
This module defines the behavior and patterns for different agent launchers (providers).
"""

from typing import List, Optional


def get_provider_key(launcher: str) -> str:
    """Get the canonical provider key for a given launcher command."""
    launcher_lower = str(launcher).lower()
    if "codex" in launcher_lower:
        return "codex"
    if "droid" in launcher_lower:
        return "droid"
    if "agent-cli" in launcher_lower:
        return "agent-cli"
    if "ccc" in launcher_lower or "claude" in launcher_lower:
        return "ccc"
    return "generic"


def resolve_launcher_command(launcher: str) -> str:
    """Resolve a launcher name to its executable command."""
    if not launcher:
        return "droid"  # Default
    return str(launcher)


def get_prompt_patterns(launcher: str) -> List[str]:
    """Get regex patterns that identify the CLI prompt for this provider."""
    key = get_provider_key(launcher)
    if key == "codex":
        return [r"›", r"❯", r"\$"]
    if key == "droid":
        return [r"\$"]
    if key == "ccc":
        return [r"❯"]
    return [r"\$", r">", r"#"]


def get_context_left_patterns(launcher: str) -> List[str]:
    """Get regex patterns that identify 'context left' or 'tokens remaining' messages."""
    key = get_provider_key(launcher)
    if key == "codex":
        return [r"(\d+)%\s+context left", r"(\d+)\s+tokens remaining"]
    if key == "ccc":
        return [
            r"(\d+)%\s+context left",
            r"(\d+)\s+tokens remaining",
            r"(\d+)\s+budget remaining",
        ]
    return [r"(\d+)%\s+context left"]


def get_session_restore_mode(launcher: str) -> str:
    """Get the restore mode for this provider (e.g. 'cli_optional_arg')."""
    key = get_provider_key(launcher)
    if key == "codex":
        return "cli_optional_arg"
    return "none"


def get_session_restore_flag(launcher: str) -> Optional[str]:
    """Get the CLI flag used for session restoration (e.g. 'resume')."""
    key = get_provider_key(launcher)
    if key == "codex":
        return "resume"
    return None


def get_system_prompt_mode(launcher: str) -> str:
    """Get the system prompt injection mode."""
    key = get_provider_key(launcher)
    if key == "codex":
        return "cli_append"
    return "tmux_paste"


def get_system_prompt_flag(launcher: str) -> Optional[str]:
    """Get the CLI flag for system prompt injection."""
    key = get_provider_key(launcher)
    if key == "codex":
        return "--prompt"
    return None


def get_system_prompt_key(launcher: str) -> Optional[str]:
    """Get the config key for system prompt injection (for cli_config_kv mode)."""
    return None


def get_agents_md_mode(launcher: str) -> str:
    """Get the AGENTS.md discovery mode ('cwd' or 'none')."""
    return "cwd"


def get_mcp_config_mode(launcher: str) -> str:
    """Get the MCP config injection mode ('cli_json' or 'none')."""
    key = get_provider_key(launcher)
    if key == "codex":
        return "cli_json"
    return "none"


def get_mcp_config_flag(launcher: str) -> Optional[str]:
    """Get the CLI flag for MCP config injection."""
    key = get_provider_key(launcher)
    if key == "codex":
        return "--mcp-config"
    return None


def get_startup_wait(launcher: str) -> float:
    """Get the initial wait time (seconds) after launching before checking for prompt."""
    return 2.0


def get_runtime_config(launcher: str) -> dict:
    """Get arbitrary runtime configuration for the provider."""
    return {}
