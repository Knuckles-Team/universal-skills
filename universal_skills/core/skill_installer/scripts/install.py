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

# Standard skill paths for various tools
TOOL_PATHS = {
    "windsurf": Path("~/.codeium/windsurf/skills").expanduser(),
    "claude": Path("~/.claude/skills").expanduser(),
    "openclaw": Path("~/.openclaw/skills").expanduser(),
    "opencode": Path("~/.config/opencode/skills").expanduser(),
    "antigravity": Path("~/.gemini/antigravity/skills").expanduser(),
}

# Workspace-specific skill paths (relative to workspace root)
WORKSPACE_PATHS = {
    "antigravity": Path(".agent/skills"),
    "default": Path(".agent/skills"),
}


def get_source_paths(
    skill_names: Optional[List[str]] = None,
    group: Optional[str] = None,
    include_graphs: bool = False,
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

    return sources


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


def install_skills(
    target_path: Path,
    skill_names: Optional[List[str]] = None,
    group: Optional[str] = None,
    force: bool = False,
    include_graphs: bool = False,
    symlink: bool = False,
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

    sources = get_source_paths(skill_names, group, include_graphs)
    if not sources:
        logger.error("No skill/graph sources found to install.")
        return False

    installed_count = 0
    for skill_src in sources:
        # Determine destination
        # Documentation graphs go into a sub-folder if they came from skill-graphs
        is_graph = "skill_graphs" in str(skill_src)
        if is_graph:
            dest_root = target_path / "skill-graphs"
            dest_root.mkdir(parents=True, exist_ok=True)
            skill_dst = dest_root / skill_src.name
        else:
            skill_dst = target_path / skill_src.name

        src_abs = skill_src.resolve()

        # Idempotent: an already-correct symlink needs no work (even without --force).
        if (
            symlink
            and skill_dst.is_symlink()
            and skill_dst.resolve() == src_abs
        ):
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
        "--tool", help="Target tool (windsurf, claude, openclaw, opencode, antigravity)"
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

    args = parser.parse_args()

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
        print("Error: Either --tool or --path must be specified.", file=sys.stderr)
        sys.exit(1)

    skill_names = args.skills.split(",") if args.skills else None

    install_skills(
        target,
        skill_names,
        args.group,
        args.force,
        args.install_skill_graphs,
        symlink=args.symlink,
    )


if __name__ == "__main__":
    main()
