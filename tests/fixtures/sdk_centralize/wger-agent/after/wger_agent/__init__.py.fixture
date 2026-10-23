#!/usr/bin/env python

import importlib
import inspect
from typing import Any

__all__: list[str] = []

CORE_MODULES: list[str] = ["wger_agent.api_client"]

OPTIONAL_MODULES = {"wger_agent.agent_server": "agent", "wger_agent.mcp_server": "mcp"}


def _expose_members(module):
    """Expose public classes and functions from a module into globals and __all__."""
    for name, obj in inspect.getmembers(module):
        if (inspect.isclass(obj) or inspect.isfunction(obj)) and not name.startswith(
            "_"
        ):
            globals()[name] = obj
            if name not in __all__:
                __all__.append(name)


# Eagerly import core modules (keeps API wrappers fast & light)
for module_name in CORE_MODULES:
    if module_name:
        module = importlib.import_module(module_name)
        _expose_members(module)

# Dynamic/lazy loading of optional modules (mcp_server)
_loaded_optional_modules: dict[str, Any] = {}


def _import_module_safely(module_name: str):
    """Try to import a module and return it, or None if not available."""
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


# Attribute names that report whether an optional module is importable, and the
# substring of its OPTIONAL_MODULES key that identifies which one each asks about.
_AVAILABILITY_MARKERS = {
    "_MCP_AVAILABLE": "mcp_server",
}


def _optional_module_available(marker: str) -> bool:
    """Report whether the OPTIONAL_MODULES entry matching marker can be imported."""
    module_key = next((k for k in OPTIONAL_MODULES if marker in k), None)
    if module_key is None:
        return False
    return _import_module_safely(module_key) is not None


def _find_in_optional_modules(name: str) -> Any:
    """Lazily import each optional module, expose its members, and return name.

    Raises AttributeError if no optional module (loaded or newly importable)
    defines the attribute.
    """
    for module_name in OPTIONAL_MODULES:
        if module_name not in _loaded_optional_modules:
            module = _import_module_safely(module_name)
            if module is not None:
                _loaded_optional_modules[module_name] = module
                _expose_members(module)

        module = _loaded_optional_modules.get(module_name)
        if module is not None and hasattr(module, name):
            return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __getattr__(name: str) -> Any:
    # Handle availability flags dynamically without eager imports
    marker = _AVAILABILITY_MARKERS.get(name)
    if marker is not None:
        return _optional_module_available(marker)

    return _find_in_optional_modules(name)


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + __all__)
