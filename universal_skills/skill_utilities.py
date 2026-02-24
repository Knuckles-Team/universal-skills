#!/usr/bin/python
# coding: utf-8

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

__version__ = "0.1.5"


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


import os

try:
    from agent_utilities.base_utilities import to_boolean
except ImportError:

    def to_boolean(val) -> bool:
        if isinstance(val, bool):
            return val
        return str(val).lower() in ("true", "1", "t", "y", "yes")


def get_universal_skills_path() -> list[str]:
    """
    Returns a list of absolute paths pointing to the individual enabled universal skills.
    Specific skills can be enabled/disabled via environment variables formatted as:
    <SKILL_DIR_NAME_UPPER_UNDERSCORES>_ENABLE=True|False
    """
    skills_dir = files(retrieve_package_name()) / "skills"
    with as_file(skills_dir) as path:
        skills_path = str(path)

    enabled_paths = []
    if os.path.exists(skills_path):
        for item in os.listdir(skills_path):
            item_path = os.path.join(skills_path, item)
            if os.path.isdir(item_path):
                env_var_name = f"{item.upper().replace('-', '_')}_ENABLE"
                is_enabled = to_boolean(os.environ.get(env_var_name, "True"))
                if is_enabled:
                    enabled_paths.append(item_path)
    return enabled_paths
