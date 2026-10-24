#!/usr/bin/env python3
"""Ontology + prompt discovery and XDG materialization.

Every installed distribution that declares an ``agent_connector_sdk.connector``
entry point contributes its ``prompts/`` and ``ontology/`` directories by
convention (``ResolvedConnector.dirs``); the SDK's ``installed_connectors()``
is the only discovery path.
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from agent_utilities.base_utilities import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
else:
    logger = get_logger(__name__)

_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")


def _xdg_data_dir() -> Path:
    """The agent-utilities XDG *data* dir, OS-aware — the unified-install root.

    Mirrors ``agent_utilities.core.paths.data_dir()`` / the ``agent-utilities``
    entry already computed in ``install.py``'s ``get_tool_paths()`` (same
    ``$XDG_DATA_HOME/agent-utilities`` convention), kept as a local copy for the
    same dependency-free-fallback reason as the rest of this module.
    """
    home = Path("~").expanduser()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", str(home / "AppData" / "Local")))
        return base / "agent-utilities"
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / "agent-utilities"
    xdg_data = Path(os.environ.get("XDG_DATA_HOME") or (home / ".local" / "share"))
    return xdg_data / "agent-utilities"


def unified_prompts_dir() -> Path:
    return _xdg_data_dir() / "prompts"


def unified_ontologies_dir() -> Path:
    return _xdg_data_dir() / "ontologies"


def iter_provider_dirs(kind: str) -> List[Tuple[str, Path]]:
    """Every installed connector's ``prompts`` or ``ontology`` directory.

    Returns ``(connector_name, directory)``. Failure-isolated: an unresolvable
    connector or a missing directory is skipped, never fatal.
    """
    try:
        from agent_connector_sdk.connector import installed_connectors

        found = installed_connectors()
    except Exception as e:  # noqa: BLE001
        logger.debug("Could not resolve installed connectors: %s", e)
        return []
    attr = {"prompts": "prompts", "ontology": "ontology"}[kind]
    return [
        (c.name, getattr(c.dirs, attr))
        for c in found
        if getattr(c.dirs, attr).is_dir()
    ]


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
    """Materialize the prompt and ontology legs from installed connectors."""
    result: Dict[str, Dict[str, int]] = {"prompts": {}, "ontologies": {}}
    if install_prompts:
        for provider, src in iter_provider_dirs("prompts"):
            if providers is not None and provider not in providers:
                continue
            try:
                result["prompts"][provider] = _copy_tree(
                    src, unified_prompts_dir() / provider, force
                )
            except OSError as e:  # noqa: BLE001
                logger.warning("Prompt provider %s not materialized: %s", provider, e)
    if install_ontologies:
        for provider, src in iter_provider_dirs("ontology"):
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
    """Materialize the prompt + ontology legs into the XDG data tree.

    Returns ``{"prompts": {connector: n}, "ontologies": {connector: n}}``; a
    skipped leg is omitted from the returned dict.
    """
    if not install_prompts and not install_ontologies:
        return {}
    return _install_local(force, providers, install_prompts, install_ontologies)
