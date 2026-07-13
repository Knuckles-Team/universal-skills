"""Console-script shim for the ``universal-installer`` skill.

The skill lives in a hyphenated directory (``core/universal-installer/``) so its
on-disk name matches its ``SKILL.md`` ``name:`` (kebab-case) — but ``-`` is not a
valid Python identifier, so ``core.universal-installer`` can never be imported by
a normal dotted path. This underscore-named module is the ``install-universal``
console-script target (see ``[project.scripts]`` in ``pyproject.toml``); it loads
the real implementation from disk by file path.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_impl_path = (
    Path(__file__).resolve().parent / "universal-installer" / "scripts" / "install.py"
)
_spec = importlib.util.spec_from_file_location(
    "universal_skills._universal_installer_impl", _impl_path
)
if _spec is None or _spec.loader is None:  # pragma: no cover - defensive
    raise ImportError(
        f"Could not load universal-installer implementation at {_impl_path}"
    )
_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_impl)

main = _impl.main
install_skills = _impl.install_skills
get_source_paths = _impl.get_source_paths
TOOL_PATHS = _impl.TOOL_PATHS
detect_present_tools = _impl.detect_present_tools
get_tool_paths = _impl.get_tool_paths

__all__ = [
    "main",
    "install_skills",
    "get_source_paths",
    "TOOL_PATHS",
    "detect_present_tools",
    "get_tool_paths",
]
