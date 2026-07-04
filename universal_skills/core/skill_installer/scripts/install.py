#!/usr/bin/env python3
import argparse
import os
import shutil
import sys
import logging
from pathlib import Path
from typing import List, Optional

try:
    from agent_utilities.base_utilities import get_logger, retrieve_package_name
except ImportError:
    # Fallback if agent_utilities is not available
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def retrieve_package_name():
        return "universal_skills"

else:
    logger = get_logger(__name__)

# Try to import utilities from the packages
try:
    from universal_skills import skill_utilities
except ImportError:
    skill_utilities = None

try:
    from skill_graphs import skill_graph_utilities
except ImportError:
    skill_graph_utilities = None


# Entry-point group through which any installed agent-package contributes its
# own skills. Kept as a standalone local copy (not imported from agent-utilities)
# so the installer still runs when agent-utilities is absent — same rationale as
# the ImportError fallbacks above. CONCEPT:OS-5.52.
SKILL_PROVIDER_GROUP = "agent_utilities.skill_providers"


def _iter_skill_providers() -> List[tuple]:
    """Resolve every ``agent_utilities.skill_providers`` entry-point to a dir.

    Returns ``(provider_name, asset_dir)`` tuples. Resolves each contributor's
    data directory via ``importlib.resources`` without importing the agent's
    business logic. Unresolvable/uninstalled providers are skipped, not fatal.
    """
    from importlib.metadata import entry_points
    from importlib.resources import as_file, files

    out: List[tuple] = []
    seen: set = set()
    try:
        eps = entry_points(group=SKILL_PROVIDER_GROUP)
    except TypeError:  # pragma: no cover - very old importlib.metadata
        eps = entry_points().get(SKILL_PROVIDER_GROUP, [])
    for ep in sorted(eps, key=lambda e: e.name):
        if ep.name in seen:
            continue
        try:
            with as_file(files(ep.value)) as resolved:
                path = Path(resolved)
            if path.is_dir():
                out.append((ep.name, path))
                seen.add(ep.name)
        except (ModuleNotFoundError, TypeError, FileNotFoundError, ValueError) as e:
            logger.debug("Could not resolve skill provider %s: %s", ep.name, e)
            continue
    return out


def get_tool_paths() -> dict:
    """Return per-tool skill-install directories, OS-aware.

    Kept in parity with the mcp-installer's tool set so a single bootstrap can
    install both skills and MCP config into every agent tool a host has. Each
    value is the *skills* directory for that tool; ``detect_present_tools()``
    decides which of these to write to in ``--all-detected`` mode.
    """
    is_windows = sys.platform == "win32"
    is_mac = sys.platform == "darwin"
    home = Path("~").expanduser()

    paths = {
        "windsurf": home / ".codeium" / "windsurf" / "skills",
        "claude": home / ".claude" / "skills",
        "openclaw": home / ".openclaw" / "skills",
        "antigravity": home / ".gemini" / "antigravity" / "skills",
        "codex": home / ".codex" / "skills",
        "devin": home / ".devin" / "skills",
        "cursor": home / ".cursor" / "skills",
    }

    # OpenCode
    if is_windows:
        appdata = Path(os.environ.get("APPDATA", "~\\AppData\\Roaming")).expanduser()
        paths["opencode"] = appdata / "opencode" / "skills"
        paths["zed"] = appdata / "Zed" / "skills"
    else:
        paths["opencode"] = home / ".config" / "opencode" / "skills"
        paths["zed"] = home / ".config" / "zed" / "skills"

    # Agent Utilities / Agent Terminal UI (shared config dir)
    if is_windows:
        localappdata = Path(
            os.environ.get("LOCALAPPDATA", "~\\AppData\\Local")
        ).expanduser()
        agent_utils_path = localappdata / "agent-utilities" / "skills"
    elif is_mac:
        agent_utils_path = (
            home / "Library" / "Application Support" / "agent-utilities" / "skills"
        )
    else:
        # XDG *data* dir (platformdirs user_data_dir), matching agent-utilities'
        # ``core.paths.skills_dir()`` which the agent factory auto-loads — NOT the
        # config dir. (macOS/Windows above already use their data dir.)
        xdg_data = Path(
            os.environ.get("XDG_DATA_HOME") or (home / ".local" / "share")
        ).expanduser()
        agent_utils_path = xdg_data / "agent-utilities" / "skills"
    paths["agent-utilities"] = agent_utils_path
    paths["agent-terminal-ui"] = agent_utils_path

    return paths


# Standard skill paths for various tools (OS-aware; parity with mcp-installer).
TOOL_PATHS = get_tool_paths()

# Workspace-specific skill paths (relative to workspace root)
WORKSPACE_PATHS = {
    "antigravity": Path(".agent/skills"),
    "default": Path(".agent/skills"),
}


def detect_present_tools() -> dict:
    """Return the subset of TOOL_PATHS whose tool is actually installed.

    A tool counts as present when the parent of its skills directory exists
    (e.g. ``~/.claude`` for Claude Code). This keeps ``--all-detected`` from
    materialising skill folders for tools the host doesn't have. Duplicate
    destinations (agent-utilities/agent-terminal-ui share a dir) are collapsed.
    """
    present: dict = {}
    seen: set = set()
    for tool, skills_dir in TOOL_PATHS.items():
        marker = skills_dir.parent
        if not marker.exists():
            continue
        resolved = str(skills_dir)
        if resolved in seen:
            continue
        seen.add(resolved)
        present[tool] = skills_dir
    return present


def _matches_layer(path: Path, layer: str) -> bool:
    """Filter a skill source path by layer.

    ``atomic`` = an atomic building-block skill (NOT under ``workflows/``) — these are
    what an agent invokes directly, so they belong in Claude. ``workflows`` = a
    skill-workflow (under ``workflows/``); these are meant for the graph-os
    orchestrator (Claude fires them via the ``kg-delegate`` skill /
    ``graph_orchestrate execute_workflow``) and usually should NOT be installed into
    Claude — that would just bloat the always-loaded skill list. ``all`` = no filter.
    """
    is_workflow = f"{os.sep}workflows{os.sep}" in f"{path}{os.sep}"
    if layer == "atomic":
        return not is_workflow
    if layer == "workflows":
        return is_workflow
    return True


def get_source_paths(
    skill_names: Optional[List[str]] = None,
    group: Optional[str] = None,
    include_graphs: bool = False,
    layer: str = "all",
) -> List[Path]:
    """Uses utility functions to locate source paths of skills and graphs."""
    sources = []

    # Universal Skills
    if skill_utilities:
        # If specific skill names provided, search for them individually
        if skill_names:
            for name in skill_names:
                paths = skill_utilities.get_universal_skills_path(name=name.strip())
                sources.extend([Path(p) for p in paths])
        # If group (category) provided, get everything in that category
        elif group:
            paths = skill_utilities.get_universal_skills_path(category=group)
            sources.extend([Path(p) for p in paths])
        # Otherwise get all
        else:
            paths = skill_utilities.get_universal_skills_path()
            sources.extend([Path(p) for p in paths])
        # Restrict to the requested layer (atomic skills vs graph-os workflows).
        if layer != "all":
            sources = [p for p in sources if _matches_layer(p, layer)]
    else:
        logger.error("Could not import skill_utilities.")

    # Skill Graphs
    if include_graphs and skill_graph_utilities:
        if skill_names:
            for name in skill_names:
                paths = skill_graph_utilities.get_skill_graphs_path(name=name.strip())
                sources.extend([Path(p) for p in paths])
        elif group:
            paths = skill_graph_utilities.get_skill_graphs_path(category=group)
            sources.extend([Path(p) for p in paths])
        else:
            paths = skill_graph_utilities.get_skill_graphs_path()
            sources.extend([Path(p) for p in paths])
    elif include_graphs:
        logger.warning("Could not import skill_graph_utilities.")

    # Package-contributed skills (entry-point providers, CONCEPT:OS-5.52).
    # Any installed agent-package that declares an ``agent_utilities.skill_providers``
    # entry-point contributes the ``SKILL.md`` dirs under its asset directory.
    wanted = {n.strip() for n in skill_names} if skill_names else None
    for _provider_name, asset_dir in _iter_skill_providers():
        for skill_md in sorted(asset_dir.rglob("SKILL.md")):
            skill_dir = skill_md.parent
            parts = skill_dir.parts
            is_graph = "skill_graphs" in parts or "skill-graphs" in parts
            # Honour the same gates as the universal-skills branch.
            if is_graph and not include_graphs:
                continue
            if wanted is not None and skill_dir.name not in wanted:
                continue
            if group and group not in parts:
                continue
            if layer != "all" and not _matches_layer(skill_dir, layer):
                continue
            sources.append(skill_dir)

    # De-dup by resolved path so a skill is never installed twice.
    seen: set = set()
    deduped: List[Path] = []
    for src in sources:
        key = str(src.resolve())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(src)
    return deduped


# Removed get_skill_graphs_source_path as it's merged into get_source_paths


def get_workspace_root() -> Optional[Path]:
    """Attempts to find the workspace root by looking for .git or other markers."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists() or (parent / ".agent").exists():
            return parent
    return current


def _remove_dest(skill_dst: Path) -> None:
    """Remove an existing destination, whether it's a symlink, file, or directory."""
    if skill_dst.is_symlink() or skill_dst.is_file():
        skill_dst.unlink()
    elif skill_dst.is_dir():
        shutil.rmtree(skill_dst)


def _try_windows_junction(dst: Path, src: Path) -> bool:
    """On Windows, create a directory JUNCTION (the symlink equivalent that needs no
    admin / Developer Mode). Returns True on success. ``mklink /J`` is a cmd builtin,
    so it must run through ``cmd /c``."""
    if os.name != "nt":
        return False
    import subprocess

    try:
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
            check=True,
            capture_output=True,
        )
        return True
    except Exception:
        return False


def install_skills(
    target_path: Path,
    skill_names: Optional[List[str]] = None,
    group: Optional[str] = None,
    force: bool = False,
    include_graphs: bool = False,
    symlink: bool = False,
    layer: str = "all",
):
    """Install skills to the target path by copy (default) or symlink.

    When ``symlink=True``, each skill is symlinked to its source in the installed
    ``universal_skills`` package instead of copied. This avoids duplicating files on disk and means
    the installed skills track the package automatically on every ``pip install -U`` — there is no
    stale copy to re-sync. Falls back to a copy if the filesystem refuses the symlink (e.g. Windows
    without privileges). This is the same pattern the bundled skills already use (e.g. the
    ``code-enhancer`` skill is a symlink into this package).
    """
    if not target_path.exists():
        logger.info(f"Creating target directory: {target_path}")
        target_path.mkdir(parents=True, exist_ok=True)

    sources = get_source_paths(skill_names, group, include_graphs, layer=layer)
    if not sources:
        logger.error("No skill/graph sources found to install.")
        return False

    installed_count = 0
    for skill_src in sources:
        # Determine destination
        # Documentation graphs go into a sub-folder, whether they came from the
        # canonical skill_graphs package or a provider's ``skill-graphs/`` subdir.
        is_graph = (
            "skill_graphs" in skill_src.parts or "skill-graphs" in skill_src.parts
        )
        if is_graph:
            dest_root = target_path / "skill-graphs"
            dest_root.mkdir(parents=True, exist_ok=True)
            skill_dst = dest_root / skill_src.name
        else:
            skill_dst = target_path / skill_src.name

        src_abs = skill_src.resolve()

        # Idempotent: an already-correct symlink needs no work (even without --force).
        if symlink and skill_dst.is_symlink() and skill_dst.resolve() == src_abs:
            logger.info(f"{skill_src.name} already symlinked → up to date.")
            continue

        if skill_dst.exists() and not force:
            logger.info(
                f"Skipping {skill_src.name} (already exists). Use --force to overwrite."
            )
            continue

        verb = "Symlinking" if symlink else "Installing"
        logger.info(f"{verb} {skill_src.name} to {skill_dst}...")
        try:
            if skill_dst.exists() or skill_dst.is_symlink():
                _remove_dest(skill_dst)
            if symlink:
                try:
                    os.symlink(src_abs, skill_dst, target_is_directory=True)
                except OSError as link_err:
                    # Windows symlinks need admin/Developer Mode; a directory
                    # junction is the no-privilege equivalent. Try it before copying.
                    if _try_windows_junction(skill_dst, src_abs):
                        logger.info(
                            f"Symlink unavailable for {skill_src.name} ({link_err}); "
                            "used a Windows directory junction instead."
                        )
                    else:
                        logger.warning(
                            f"Symlink unavailable for {skill_src.name} ({link_err}); copying instead."
                        )
                        shutil.copytree(src_abs, skill_dst)
            else:
                shutil.copytree(src_abs, skill_dst)
            installed_count += 1
        except Exception as e:
            logger.error(f"Failed to install {skill_src.name}: {e}")

    mode = "symlinked" if symlink else "installed"
    logger.info(f"Successfully {mode} {installed_count} items.")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Install universal-skills into agent tools"
    )
    parser.add_argument(
        "--tool",
        help=("Target tool: " + ", ".join(sorted(TOOL_PATHS)) + "."),
    )
    parser.add_argument(
        "--all-detected",
        action="store_true",
        help="Install into every agent tool detected on this host (skips absent tools).",
    )
    parser.add_argument(
        "--all",
        dest="all_tools",
        action="store_true",
        help="Install into every known tool path whether or not it is detected.",
    )
    parser.add_argument("--path", help="Explicit custom path to install skills into")
    parser.add_argument(
        "--scope",
        choices=["global", "workspace"],
        default="global",
        help="Installation scope (default: global)",
    )
    parser.add_argument(
        "--skills", help="Comma-separated list of skill names to install (default: all)"
    )
    parser.add_argument(
        "--group", "--category", help="Install all skills in a specific category"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing skills"
    )
    parser.add_argument(
        "--symlink",
        "--link",
        action="store_true",
        help=(
            "Symlink skills to the installed universal_skills package instead of copying. "
            "No duplicate files; skills auto-update on every 'pip install -U universal-skills'."
        ),
    )
    parser.add_argument(
        "--install-skill-graphs",
        action="store_true",
        help="Also install skill-graphs from the skill-graphs repository",
    )
    parser.add_argument(
        "--layer",
        choices=["all", "atomic", "workflows"],
        default="all",
        help=(
            "Which layer to install. 'atomic' = atomic building-block skills only "
            "(recommended for Claude — the agent invokes these directly). 'workflows' "
            "= skill-workflows only (these run on the graph-os orchestrator; Claude "
            "fires them via kg-delegate). 'all' = both (default)."
        ),
    )

    args = parser.parse_args()

    skill_names = args.skills.split(",") if args.skills else None

    # Fan-out modes: install into many tool dirs in one shot.
    if args.all_detected or args.all_tools:
        targets = detect_present_tools() if args.all_detected else dict(TOOL_PATHS)
        if not targets:
            print(
                "No agent tools detected on this host. Use --tool/--path to target one "
                "explicitly, or --all to install into every known path.",
                file=sys.stderr,
            )
            sys.exit(1)
        # Collapse duplicate destinations (e.g. agent-utilities/agent-terminal-ui).
        seen: set = set()
        for tool, target in targets.items():
            if str(target) in seen:
                continue
            seen.add(str(target))
            logger.info(f"→ {tool}: {target}")
            install_skills(
                target,
                skill_names,
                args.group,
                args.force,
                args.install_skill_graphs,
                symlink=args.symlink,
                layer=args.layer,
            )
        return

    if args.path:
        target = Path(args.path).expanduser()
    elif args.tool:
        tool_key = args.tool.lower()
        if args.scope == "global":
            target = TOOL_PATHS.get(tool_key)
            if not target:
                # Fallback to treating tool as a path if not found in TOOL_PATHS
                target = Path(args.tool).expanduser()
        else:  # workspace scope
            root = get_workspace_root()
            rel_path = WORKSPACE_PATHS.get(tool_key, WORKSPACE_PATHS["default"])
            target = root / rel_path
    else:
        print(
            "Error: one of --tool / --path / --all-detected / --all must be specified.",
            file=sys.stderr,
        )
        sys.exit(1)

    install_skills(
        target,
        skill_names,
        args.group,
        args.force,
        args.install_skill_graphs,
        symlink=args.symlink,
        layer=args.layer,
    )


if __name__ == "__main__":
    main()
