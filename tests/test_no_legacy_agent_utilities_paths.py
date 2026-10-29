"""Shipped skills and installers never name the legacy agent-utilities directories."""

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "universal_skills" / "skills"

# Config, data, cache and state locations (and their env var) of the legacy app name.
LEGACY = re.compile(
    r"\.config/agent-utilities"
    r"|\$XDG_[A-Z]+_HOME/agent-utilities"
    r"|Application Support/agent-utilities"
    r'|/ "agent-utilities" / "(skills|mcp_config\.json)"'
    r"|AGENT_UTILITIES_CONFIG_DIR"
)


def _shipped_files():
    for base in (SKILLS, ROOT / "install.sh", ROOT / "install.ps1", ROOT / "AGENTS.md"):
        paths = [base] if base.is_file() else base.rglob("*")
        for path in paths:
            if path.is_file() and path.suffix in {".py", ".md", ".sh", ".ps1", ".json", ".yaml", ".yml"}:
                yield path


def test_no_shipped_file_names_a_legacy_agent_utilities_path():
    offenders = [
        str(path.relative_to(ROOT))
        for path in _shipped_files()
        if path.resolve() != Path(__file__).resolve()
        and LEGACY.search(path.read_text("utf-8", errors="ignore"))
    ]
    assert offenders == []


def _load(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, str(SKILLS / relative))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_mcp_installer_targets_the_arbora_config_dir():
    module = _load("mcp-installer/scripts/install.py", "_mcp_installer_paths")
    paths = module.get_tool_paths() if hasattr(module, "get_tool_paths") else {}
    assert "agent-utilities" not in paths
    assert all("agent-utilities" not in str(p) for p in paths.values())
