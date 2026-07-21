#!/usr/bin/env python3
"""Install skills/prompts/ontologies directly from an ``agents/*`` checkout.

For a package that is already pip-installed, the standard entry-point
discovery in ``install.py``/``providers.py`` is enough. This module covers the
other case named in the task: a checkout being developed against that has
**not** been pip-installed yet — parse its own ``pyproject.toml`` directly
(stdlib ``tomllib``, no network/pip involved) to resolve the same
``agent_utilities.{skill,prompt,ontology}_providers`` entry-points and its
``*-mcp`` console scripts, straight from source.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - repo requires-python >=3.11
    tomllib = None

try:
    from agent_utilities.base_utilities import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
else:
    logger = get_logger(__name__)

SKILL_PROVIDER_GROUP = "agent_utilities.skill_providers"
PROMPT_PROVIDER_GROUP = "agent_utilities.prompt_providers"
ONTOLOGY_PROVIDER_GROUP = "agent_utilities.ontology_providers"


class PackageManifest:
    """Parsed view of one ``agents/*`` checkout's ``pyproject.toml``."""

    def __init__(self, pkg_path: Path, data: dict):
        self.pkg_path = pkg_path
        self.data = data

    @property
    def name(self) -> str:
        return str(self.data.get("project", {}).get("name", self.pkg_path.name))

    def _entry_point_dir(self, group: str) -> Optional[Path]:
        """Resolve ``[project.entry-points."<group>"]`` (this package's own single
        entry, keyed by any name) to a source directory inside the checkout.

        The entry-point value is a dotted module path (e.g. ``gitlab_api.skills``)
        which — for a standard ``src``-less or ``src/``-layout package — maps
        onto ``<pkg_path>/<module>/<submodule>`` or ``<pkg_path>/src/<module>/
        <submodule>``. Both are tried; the first that exists wins. Never
        invented: only returns a path that actually exists on disk.
        """
        eps = self.data.get("project", {}).get("entry-points", {}).get(group, {})
        if not eps:
            return None
        # A provider group declares exactly one contribution for its own package.
        dotted = next(iter(eps.values()))
        rel = Path(*dotted.split("."))
        for base in (self.pkg_path, self.pkg_path / "src"):
            candidate = base / rel
            if candidate.is_dir():
                return candidate
        return None

    def skills_dir(self) -> Optional[Path]:
        return self._entry_point_dir(SKILL_PROVIDER_GROUP)

    def prompts_dir(self) -> Optional[Path]:
        return self._entry_point_dir(PROMPT_PROVIDER_GROUP)

    def ontology_dir(self) -> Optional[Path]:
        return self._entry_point_dir(ONTOLOGY_PROVIDER_GROUP)

    def mcp_console_scripts(self) -> List[str]:
        """``*-mcp`` entries from this package's own ``[project.scripts]`` table —
        read from source, never guessed from the package name."""
        scripts = self.data.get("project", {}).get("scripts", {})
        return sorted(name for name in scripts if name.endswith("-mcp"))


def load_manifest(pkg_path: Path) -> Optional[PackageManifest]:
    """Parse ``<pkg_path>/pyproject.toml``. Returns ``None`` if unreadable."""
    if tomllib is None:  # pragma: no cover - requires-python >=3.11 guards this
        logger.error("tomllib unavailable (Python < 3.11); cannot parse pyproject.toml.")
        return None
    pyproject = pkg_path / "pyproject.toml"
    if not pyproject.is_file():
        logger.error("No pyproject.toml found at %s", pkg_path)
        return None
    try:
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
    except Exception as e:  # noqa: BLE001
        logger.error("Could not parse %s: %s", pyproject, e)
        return None
    return PackageManifest(pkg_path.resolve(), data)


def discover_skill_sources(manifest: PackageManifest) -> List[Path]:
    """Every ``SKILL.md``-bearing directory under the package's declared skills dir."""
    skills_dir = manifest.skills_dir()
    if skills_dir is None:
        return []
    return sorted({p.parent for p in skills_dir.rglob("SKILL.md")})


def summarize(manifest: PackageManifest) -> Dict[str, object]:
    return {
        "name": manifest.name,
        "skills": len(discover_skill_sources(manifest)),
        "prompts_dir": str(manifest.prompts_dir()) if manifest.prompts_dir() else None,
        "ontology_dir": (
            str(manifest.ontology_dir()) if manifest.ontology_dir() else None
        ),
        "mcp_console_scripts": manifest.mcp_console_scripts(),
    }
