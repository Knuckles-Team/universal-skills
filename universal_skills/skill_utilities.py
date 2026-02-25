#!/usr/bin/python
# coding: utf-8

import os
from pathlib import Path
from importlib.resources import files, as_file

try:
    from openai import AsyncOpenAI
    from pydantic_ai.providers.openai import OpenAIProvider
except ImportError:
    AsyncOpenAI = None
    OpenAIProvider = None

try:
    from groq import AsyncGroq
    from pydantic_ai.providers.groq import GroqProvider
except ImportError:
    AsyncGroq = None
    GroqProvider = None

try:
    from mistralai import Mistral
    from pydantic_ai.providers.mistral import MistralProvider
except ImportError:
    Mistral = None
    MistralProvider = None

try:
    from pydantic_ai.models.anthropic import AnthropicModel
    from anthropic import AsyncAnthropic
    from pydantic_ai.providers.anthropic import AnthropicProvider
except ImportError:
    AnthropicModel = None
    AsyncAnthropic = None
    AnthropicProvider = None

__version__ = "0.1.7"


def retrieve_package_name() -> str:
    """
    Returns the top-level package name of the module that imported this utils.py.

    Works reliably when utils.py is inside a proper package (with __init__.py or
    implicit namespace package) and the caller does normal imports.
    """
    if __package__:
        top = __package__.partition(".")[0]
        if top and top != "__main__":
            return top

    try:
        file_path = Path(__file__).resolve()
        for parent in file_path.parents:
            if (
                (parent / "pyproject.toml").is_file()
                or (parent / "setup.py").is_file()
                or (parent / "__init__.py").is_file()
            ):
                return parent.name
    except Exception:
        pass

    return "unknown_package"


try:
    from agent_utilities.base_utilities import to_boolean
except ImportError:

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
    "web-searching": True,
    # Documentation graphs are False by default globally, but can be overridden here if needed.
}


def _get_enabled_paths(sub_dir: str, default_enabled: bool = True) -> list[str]:
    """
    Helper to return absolute paths of items in a sub-directory that are enabled via env vars.
    Checks inside the package directory.
    """
    base_dir = files(retrieve_package_name()) / sub_dir
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


def get_universal_skills_path() -> list[str]:
    """
    Returns a list of absolute paths pointing to the individual enabled universal skills.
    Specific skills can be enabled/disabled via environment variables formatted as:
    <SKILL_DIR_NAME_UPPER_UNDERSCORES>_ENABLE=True|False
    """
    return _get_enabled_paths("skills", default_enabled=True)


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
