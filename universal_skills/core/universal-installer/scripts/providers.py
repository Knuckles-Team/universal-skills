#!/usr/bin/env python3
"""Ontology + prompt provider discovery and XDG materialization.

The skill/skill-graph leg (``install.py``) resolves the skill-provider
entry-point locally. This module does the same for the other two legs of the
federation: the prompt-provider and ontology-provider entry-point groups
(``PROMPT_PROVIDER_GROUP`` / ``ONTOLOGY_PROVIDER_GROUP`` below).

Resolution and materialization are local and dependency-free, so this skill
works in any environment that has universal-skills installed.
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from agent_connector_sdk.utilities import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
else:
    logger = get_logger(__name__)

# Published plugin entry-point group names (the contract provider packages
# declare); they are strings, not an import of any package.
PROMPT_PROVIDER_GROUP = "agent_utilities.prompt_providers"
ONTOLOGY_PROVIDER_GROUP = "agent_utilities.ontology_providers"

_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")


def _xdg_data_dir() -> Path:
    """The graph-os XDG *data* dir, OS-aware — the unified-install root.

    Mirrors the ``graph-os``
    entry already computed in ``install.py``'s ``get_tool_paths()`` (same
    ``$XDG_DATA_HOME/graph-os`` convention), kept as a local copy for the
    same dependency-free-fallback reason as the rest of this module.
    """
    home = Path("~").expanduser()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", str(home / "AppData" / "Local")))
        return base / "graph-os"
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / "graph-os"
    xdg_data = Path(os.environ.get("XDG_DATA_HOME") or (home / ".local" / "share"))
    return xdg_data / "graph-os"


def unified_prompts_dir() -> Path:
    return _xdg_data_dir() / "prompts"


def unified_ontologies_dir() -> Path:
    return _xdg_data_dir() / "ontologies"


def iter_provider_dirs(group: str) -> List[Tuple[str, Path]]:
    """Resolve every entry-point in ``group`` to ``(provider_name, asset_dir)``.

    Failure-isolated: an unresolvable provider (not installed, bad value,
    missing directory) is skipped, never fatal — one broken package can't break
    discovery for the rest of the fleet.
    """
    from importlib.metadata import entry_points
    from importlib.resources import as_file, files

    out: List[Tuple[str, Path]] = []
    seen: set = set()
    try:
        eps = entry_points(group=group)
    except TypeError:  # pragma: no cover - very old importlib.metadata
        eps = entry_points().get(group, [])
    for ep in sorted(eps, key=lambda e: e.name):
        if ep.name in seen:
            continue
        try:
            with as_file(files(ep.value)) as resolved:
                path = Path(resolved)
            if path.is_dir():
                out.append((ep.name, path))
                seen.add(ep.name)
        except Exception as e:  # noqa: BLE001
            logger.debug("Could not resolve provider %s (%s): %s", ep.name, group, e)
            continue
    return out


def _copy_tree(src: Path, dst: Path, force: bool) -> int:
    """Copy a provider's whole prompt asset directory. Returns files copied."""
    if not src.is_dir():
        return 0
    if dst.exists():
        if not force:
            return 0
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=_IGNORE)
    return sum(1 for p in dst.rglob("*") if p.is_file())


def _copy_ontology(src: Path, dst: Path, force: bool) -> int:
    """Materialize a provider's ``*.ttl`` (+ ``shapes/*.ttl``). Returns count."""
    ttls = sorted(src.glob("*.ttl"))
    shapes_src = src / "shapes"
    shapes = sorted(shapes_src.glob("*.ttl")) if shapes_src.is_dir() else []
    if not ttls and not shapes:
        return 0
    if dst.exists():
        if not force:
            return 0
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)
    n = 0
    for t in ttls:
        shutil.copy2(t, dst / t.name)
        n += 1
    if shapes:
        (dst / "shapes").mkdir(parents=True, exist_ok=True)
        for s in shapes:
            shutil.copy2(s, dst / "shapes" / s.name)
            n += 1
    return n


def _install_local(
    force: bool,
    providers: Optional[set],
    install_prompts: bool,
    install_ontologies: bool,
) -> Dict[str, Dict[str, int]]:
    """Dependency-free fallback materialization ."""
    result: Dict[str, Dict[str, int]] = {"prompts": {}, "ontologies": {}}
    if install_prompts:
        for provider, src in iter_provider_dirs(PROMPT_PROVIDER_GROUP):
            if providers is not None and provider not in providers:
                continue
            try:
                result["prompts"][provider] = _copy_tree(
                    src, unified_prompts_dir() / provider, force
                )
            except OSError as e:  # noqa: BLE001
                logger.warning("Prompt provider %s not materialized: %s", provider, e)
    if install_ontologies:
        for provider, src in iter_provider_dirs(ONTOLOGY_PROVIDER_GROUP):
            if providers is not None and provider not in providers:
                continue
            try:
                result["ontologies"][provider] = _copy_ontology(
                    src, unified_ontologies_dir() / provider, force
                )
            except OSError as e:  # noqa: BLE001
                logger.warning(
                    "Ontology provider %s not materialized: %s", provider, e
                )
    return result


def install_ontologies_and_prompts(
    force: bool = True,
    providers: Optional[set] = None,
    install_prompts: bool = True,
    install_ontologies: bool = True,
) -> Dict[str, Any]:
    """Materialize the prompt + ontology legs into the graph-os XDG tree.

    Uses the local, dependency-free resolver above. Returns
    ``{"prompts": {provider: n}, "ontologies": {provider: n}}``; a skipped leg
    (``install_prompts=False`` / ``install_ontologies=False``) is omitted from
    the returned dict for that key.
    """
    if not install_prompts and not install_ontologies:
        return {}
    return _install_local(force, providers, install_prompts, install_ontologies)
