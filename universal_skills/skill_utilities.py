#!/usr/bin/python
# coding: utf-8

import os
from pathlib import Path
from importlib.resources import files, as_file
from typing import Optional

try:
    from openai import AsyncOpenAI
    from pydantic_ai.providers.openai import OpenAIProvider
except ImportError:
    AsyncOpenAI = None  # type: ignore
    OpenAIProvider = None  # type: ignore

try:
    from groq import AsyncGroq
    from pydantic_ai.providers.groq import GroqProvider
except ImportError:
    AsyncGroq = None  # type: ignore
    GroqProvider = None  # type: ignore

try:
    from mistralai import Mistral
    from pydantic_ai.providers.mistral import MistralProvider
except ImportError:
    Mistral = None  # type: ignore
    MistralProvider = None  # type: ignore

try:
    from pydantic_ai.models.anthropic import AnthropicModel
    from anthropic import AsyncAnthropic
    from pydantic_ai.providers.anthropic import AnthropicProvider
except ImportError:
    AnthropicModel = None  # type: ignore
    AsyncAnthropic = None  # type: ignore
    AnthropicProvider = None  # type: ignore

__version__ = "0.7.0"


def get_universal_skills_package_name() -> str:
    """
    Returns the package name of universal_skills.
    """
    return "universal_skills"


def to_boolean(val) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "1", "t", "y", "yes")


# Default enablement state for specific skills or skill-graphs.
# If a skill/graph is not listed here, it follows the global default for its category.
SKILL_DEFAULTS = {
    # Niche skills disabled by default
    "cloudflare-deploy": False,
    "google-workspace": False,
    "jupyter-notebook": False,
    "skill-graph-builder": True,
    "web-crawler": True,
    "web-search": True,
    "tdd-methodology": True,
    "manual-testing-enhanced": True,
    "code-walkthrough": True,
    "interactive-explain": True,
}


def _get_enabled_paths(sub_dir: str, default_enabled: bool = True) -> list[str]:
    """
    Helper to return absolute paths of items in a sub-directory that are enabled via env vars.
    Checks inside the package directory.
    """
    base_dir = files(get_universal_skills_package_name()) / sub_dir
    with as_file(base_dir) as path:
        abs_path = str(path)

    enabled_paths = []
    if os.path.exists(abs_path):
        for item in os.listdir(abs_path):
            item_path = os.path.join(abs_path, item)
            if os.path.isdir(item_path):
                # Check for specific override in SKILL_DEFAULTS
                item_default = SKILL_DEFAULTS.get(item, default_enabled)

                env_var_name = f"{item.upper().replace('-', '_')}_ENABLE"
                is_enabled = to_boolean(os.environ.get(env_var_name, item_default))
                if is_enabled:
                    enabled_paths.append(item_path)
    return enabled_paths


def get_universal_skills_path(
    category: Optional[str] = None, name: Optional[str] = None
) -> list[str]:
    """
    Returns a list of absolute paths pointing to the individual enabled universal skills.
    Specific skills can be enabled/disabled via environment variables formatted as:
    <SKILL_DIR_NAME_UPPER_UNDERSCORES>_ENABLE=True|False

    Args:
        category: Optional category folder name (e.g. 'web-dev')
        name: Optional single skill name (e.g. 'web-search')
    """
    package_name = get_universal_skills_package_name()
    # The package root is now the collection of categories
    base_dir = files(package_name)

    try:
        with as_file(base_dir) as path:
            abs_root_path = Path(path)
    except Exception:
        return []

    if not abs_root_path.exists():
        return []

    enabled_paths = []

    # Helper to check if a directory is a valid skill (contains SKILL.md or is a leaf)
    def is_skill_dir(p: Path) -> bool:
        return p.is_dir() and (p / "SKILL.md").exists()

    # If a specific name is requested, search recursively across all subdirectories
    if name:
        for p in abs_root_path.rglob(name):
            if is_skill_dir(p):
                # Check if enabled
                item_default = SKILL_DEFAULTS.get(name, True)
                env_var_name = f"{name.upper().replace('-', '_')}_ENABLE"
                if to_boolean(os.environ.get(env_var_name, item_default)):
                    enabled_paths.append(str(p.resolve()))
                return enabled_paths  # Found (even if disabled), stop search
        return []

    # If a category is requested, just search that one. Otherwise, search all.
    if category:
        cat_dir = abs_root_path / category
        if cat_dir.is_dir():
            for skill_dir in cat_dir.iterdir():
                if is_skill_dir(skill_dir):
                    item_name = skill_dir.name
                    item_default = SKILL_DEFAULTS.get(item_name, True)
                    env_var_name = f"{item_name.upper().replace('-', '_')}_ENABLE"
                    if to_boolean(os.environ.get(env_var_name, item_default)):
                        enabled_paths.append(str(skill_dir.resolve()))
        return enabled_paths

    # Get All: Recursively find all skill directories
    for p in abs_root_path.rglob("*"):
        if is_skill_dir(p):
            item_name = p.name
            item_default = SKILL_DEFAULTS.get(item_name, True)
            env_var_name = f"{item_name.upper().replace('-', '_')}_ENABLE"
            if to_boolean(os.environ.get(env_var_name, item_default)):
                enabled_paths.append(str(p.resolve()))

    return enabled_paths


def get_skill_graph_path() -> list[str]:
    """
    Returns a list of absolute paths pointing to the individual enabled skill-graphs.
    Specific skill-graphs can be enabled/disabled via environment variables formatted as:
    <GRAPH_DIR_NAME_UPPER_UNDERSCORES>_ENABLE=True|False

    This scans the user's cache directory (~/.cache/universal-skills/skill-graphs)
    for subdirectories and includes them if their corresponding enable flag is set.
    """
    cache_base = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
    cache_dir = Path(cache_base) / "universal-skills" / "skill-graphs"

    enabled_paths = []
    if cache_dir.exists() and cache_dir.is_dir():
        for item in os.listdir(cache_dir):
            item_path = cache_dir / item
            if item_path.is_dir():
                # Default to False for skill-graphs unless explicitly enabled
                env_var_name = f"{item.upper().replace('-', '_')}_ENABLE"
                is_enabled = to_boolean(os.environ.get(env_var_name, False))
                if is_enabled:
                    enabled_paths.append(str(item_path.resolve()))

    return enabled_paths


def resolve_mcp_reference(filename: str) -> Optional[str]:
    """
    Resolves an MCP configuration filename to its absolute path within the mcp-client skill.
    Supports .json, .md, and extensionless filenames (defaults to .json).
    """
    if not filename:
        return None

    # Check if it's already an absolute or relative path that exists
    if os.path.exists(filename):
        return str(Path(filename).resolve())

    try:
        # Standardize filename: if no extension, default to .json
        # If it has an extension (like .md), keep it.
        has_extension = any(filename.endswith(ext) for ext in [".json", ".md"])
        target_file = filename if has_extension else f"{filename}.json"

        # Resolve via importlib.resources
        ref_base = (
            files(get_universal_skills_package_name())
            / "agent-tools"
            / "mcp-client"
            / "references"
            / target_file
        )
        with as_file(ref_base) as path:
            if path.exists():
                return str(path)
    except Exception as e:
        import logging

        logging.getLogger(__name__).debug(
            f"Error resolving MCP reference {filename}: {e}"
        )

    return None
