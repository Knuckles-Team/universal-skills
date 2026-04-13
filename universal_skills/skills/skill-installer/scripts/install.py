#!/usr/bin/env python3
import argparse
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


def get_universal_skills_source_path() -> Path:
    """Locates the source directory of the universal skills."""
    # Try via package metadata (this works for pip-installed packages)
    try:
        from importlib.resources import files

        with files("universal_skills").joinpath("skills") as p:
            if p.exists():
                return p
    except Exception:
        pass

    # If we still can't find the package, check common source locations
    try:
        from pathlib import Path

        # Check if we're running from the source directory (common in development)
        script_dir = Path(__file__).parent.parent.parent
        possible_sources = [
            script_dir,
            Path(
                "/home/genius/Workspace/agent-packages/universal-skills/universal_skills/skills"
            ),
        ]

        for source_path in possible_sources:
            if source_path.exists() and source_path.is_dir():
                # Verify it looks like a skills directory by checking for a few skill directories
                if any(
                    (source_path / skill).exists()
                    for skill in ["web-search", "agent-builder"]
                    if (source_path / skill).is_dir()
                ):
                    return source_path
    except Exception:
        pass

    # If we still can't find the package, return None
    # The skill should be installed via pip for this to work
    return None


def get_skill_graphs_source_path() -> Path:
    """Locates the source directory of the skill graphs."""
    # Try via package metadata (this works for pip-installed packages)
    try:
        from importlib.resources import files

        with files("skill_graphs").joinpath("skill_graphs") as p:
            if p.exists():
                return p
    except Exception:
        pass

    # If we still can't find the package, check common source locations
    try:
        from pathlib import Path

        # Check if we're running from the source directory (common in development)
        script_dir = Path(__file__).parent.parent.parent
        possible_sources = [
            script_dir,
            Path(
                "/home/genius/Workspace/agent-packages/skills/skill-graphs/skill_graphs/skill_graphs"
            ),
        ]

        for source_path in possible_sources:
            if source_path.exists() and source_path.is_dir():
                # Verify it looks like a skill_graphs directory by checking for a few skill directories
                if any(
                    (source_path / skill).exists()
                    for skill in ["aws-docs", "azure-docs"]
                    if (source_path / skill).is_dir()
                ):
                    return source_path
    except Exception:
        pass

    # If we still can't find the package, return None
    # The skill should be installed via pip for this to work
    return None


def get_workspace_root() -> Optional[Path]:
    """Attempts to find the workspace root by looking for .git or other markers."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists() or (parent / ".agent").exists():
            return parent
    return current


def install_skills(
    target_path: Path,
    skill_names: Optional[List[str]] = None,
    force: bool = False,
    install_skill_graphs: bool = False,
):
    """Copies skills to the target path."""
    # Install universal skills
    source_dir = get_universal_skills_source_path()
    if not source_dir:
        logger.error("Could not locate universal-skills source directory.")
        return False

    if not target_path.exists():
        logger.info(f"Creating target directory: {target_path}")
        target_path.mkdir(parents=True, exist_ok=True)

    # Get available skills (directories with SKILL.md)
    available_skills = [
        d for d in source_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()
    ]

    if skill_names:
        skills_to_install = [d for d in available_skills if d.name in skill_names]
        if not skills_to_install:
            logger.warning(f"None of the specified skills {skill_names} were found.")
            return False
    else:
        skills_to_install = available_skills

    installed_count = 0
    for skill_src in skills_to_install:
        skill_dst = target_path / skill_src.name
        if skill_dst.exists() and not force:
            logger.info(
                f"Skipping {skill_src.name} (already exists). Use --force to overwrite."
            )
            continue

        logger.info(f"Installing {skill_src.name} to {skill_dst}...")
        try:
            if skill_dst.exists():
                shutil.rmtree(skill_dst)
            shutil.copytree(skill_src, skill_dst)
            installed_count += 1
        except Exception as e:
            logger.error(f"Failed to install {skill_src.name}: {e}")

    # Install skill graphs if requested
    if install_skill_graphs:
        skill_graphs_dir = get_skill_graphs_source_path()
        if not skill_graphs_dir:
            logger.warning("Could not locate skill-graphs source directory.")
        else:
            # Create skill-graphs directory in target if it doesn't exist
            skill_graphs_target = target_path / "skill-graphs"
            if not skill_graphs_target.exists():
                logger.info(f"Creating skill-graphs directory: {skill_graphs_target}")
                skill_graphs_target.mkdir(parents=True, exist_ok=True)

            # Get available skill graphs (directories)
            available_skill_graphs = [
                d for d in skill_graphs_dir.iterdir() if d.is_dir()
            ]

            for skill_graph_src in available_skill_graphs:
                skill_graph_dst = skill_graphs_target / skill_graph_src.name
                if skill_graph_dst.exists() and not force:
                    logger.info(
                        f"Skipping skill-graph {skill_graph_src.name} (already exists). Use --force to overwrite."
                    )
                    continue

                logger.info(
                    f"Installing skill-graph {skill_graph_src.name} to {skill_graph_dst}..."
                )
                try:
                    if skill_graph_dst.exists():
                        shutil.rmtree(skill_graph_dst)
                    shutil.copytree(skill_graph_src, skill_graph_dst)
                    installed_count += 1
                except Exception as e:
                    logger.error(
                        f"Failed to install skill-graph {skill_graph_src.name}: {e}"
                    )

    logger.info(f"Successfully installed {installed_count} skills and skill-graphs.")
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
        "--force", action="store_true", help="Overwrite existing skills"
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

    install_skills(target, skill_names, args.force, args.install_skill_graphs)


if __name__ == "__main__":
    main()
