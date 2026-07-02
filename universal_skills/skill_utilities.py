#!/usr/bin/python
# coding: utf-8

import hashlib
import os
import re
from pathlib import Path
from importlib.resources import files, as_file
from typing import Iterable, Optional


__version__ = "1.0.1"


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
    "skill-workflow-builder": True,
    "web-crawler": True,
    "web-search": True,
    "tdd-methodology": True,
    "manual-testing-enhanced": True,
    "code-walkthrough": True,
    "interactive-explain": True,
    "analyze_portainer_health": True,
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


# --------------------------------------------------------------------------- #
# Cross-platform path safety (Windows / macOS / Linux)                          #
# --------------------------------------------------------------------------- #
# Filenames that are illegal on Windows (NTFS) regardless of extension.
_WIN_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
# Reserved DOS device names (case-insensitive), with or without an extension.
_WIN_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
# Conservative caps so a deep tree still fits Windows MAX_PATH (260) and every
# common filesystem's 255-byte component limit.
DEFAULT_MAX_NAME = 80
DEFAULT_MAX_RELPATH = 180


def portable_name(name: str, *, max_len: int = DEFAULT_MAX_NAME) -> str:
    """Return a single path component safe on Windows, macOS, and Linux.

    Strips Windows-illegal characters and control codes, removes trailing dots /
    spaces (silently dropped by Windows), guards reserved device names, and
    length-bounds the component — over-long names are truncated and suffixed with a
    short content hash so distinct originals stay distinct. The extension (one level)
    is preserved across truncation.
    """
    if not name:
        return "_"
    cleaned = _WIN_ILLEGAL.sub("-", name).rstrip(". ").lstrip(" ")
    cleaned = cleaned.replace("~", "-") or "_"
    stem, dot, ext = cleaned.rpartition(".")
    base, suffix = (stem, dot + ext) if dot and stem else (cleaned, "")
    if base.upper() in _WIN_RESERVED:
        base = f"{base}_"
    full = f"{base}{suffix}"
    if len(full) > max_len:
        digest = hashlib.sha1(name.encode("utf-8"), usedforsecurity=False).hexdigest()[
            :8
        ]
        keep = max(1, max_len - len(suffix) - 9)  # 9 = '-' + 8-char hash
        full = f"{base[:keep]}-{digest}{suffix}"
    return full or "_"


def portable_relpath(
    parts: Iterable[str],
    *,
    max_name: int = DEFAULT_MAX_NAME,
    max_total: int = DEFAULT_MAX_RELPATH,
) -> str:
    """Join path ``parts`` into a portable POSIX relative path within length caps.

    Each component is run through :func:`portable_name`; if the joined path still
    exceeds ``max_total`` the **last** component (the filename) is re-truncated
    harder, preserving its extension, so the whole relative path fits even on
    Windows MAX_PATH-constrained checkouts.
    """
    safe = [portable_name(p, max_len=max_name) for p in parts if p not in ("", ".")]
    if not safe:
        return "_"
    joined = "/".join(safe)
    if len(joined) <= max_total:
        return joined
    prefix = "/".join(safe[:-1])
    budget = max(8, max_total - len(prefix) - 1)
    safe[-1] = portable_name(safe[-1], max_len=budget)
    return "/".join(safe)


def dedupe_caseless(names: Iterable[str]) -> dict[str, str]:
    """Map each name to a case-insensitively unique name (macOS/Windows safe).

    Two files differing only in case (``Queues.md`` vs ``queues.md``) collide on
    case-insensitive volumes; the second and later collisions get a ``-2``/``-3`` …
    suffix (before the extension). Returns ``{original: deduped}``.
    """
    seen: dict[str, int] = {}
    out: dict[str, str] = {}
    for name in names:
        key = name.lower()
        if key not in seen:
            seen[key] = 1
            out[name] = name
            continue
        seen[key] += 1
        stem, dot, ext = name.rpartition(".")
        base, suffix = (stem, dot + ext) if dot and stem else (name, "")
        out[name] = f"{base}-{seen[key]}{suffix}"
    return out
