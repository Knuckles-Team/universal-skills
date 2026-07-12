"""Backward-compat bridge: the ``skill-installer`` skill is now ``universal-installer``.

Kept as a thin re-export — NOT a second implementation — solely because
``universal_skills.core.skill_installer`` is a cross-repo Python import contract:
``agent-utilities``' CLI (``agent_utilities/cli/__init__.py``) imports
``from universal_skills.core.skill_installer.scripts import install`` directly, and
several ``agents/*`` packages depend on the ``universal-skills[skill-installer]``
pip extra. Renaming this module out from under them is out of scope for this
skill's own repo (it would require synchronized changes across those other
governed repos). Everything here delegates to the real implementation in
``universal_installer.py`` / ``core/universal-installer/scripts/install.py`` — see
that module's docstring. The ``install-skills`` console script (see
``[project.scripts]``) still resolves through this bridge; ``install-universal``
is the primary, current name.
"""

from __future__ import annotations

from universal_skills.core.universal_installer import (
    TOOL_PATHS,
    detect_present_tools,
    get_source_paths,
    get_tool_paths,
    install_skills,
    main,
)

__all__ = [
    "main",
    "install_skills",
    "get_source_paths",
    "TOOL_PATHS",
    "detect_present_tools",
    "get_tool_paths",
]
