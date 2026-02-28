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
    "antigravity": Path("~/.agents/skills").expanduser(),
}


def get_universal_skills_source_path() -> Path:
    """Locates the source directory of the universal skills."""
    # Try relative to this script
    script_dir = Path(__file__).parent.parent.parent
    if (script_dir / "web-search").exists():
        return script_dir

    # Try via package metadata
    try:
        from importlib.resources import files

        source = files("universal_skills") / "skills"
        with source.as_file() as p:
            if p.exists():
                return p
    except Exception:
        pass

    # Fallback to current workspace structure
    workspace_path = Path(
        "/home/genius/Workspace/agent-packages/universal-skills/universal_skills/skills"
    )
    if workspace_path.exists():
        return workspace_path

    return None


def install_skills(
    target_path: Path, skill_names: Optional[List[str]] = None, force: bool = False
):
    """Copies skills to the target path."""
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

    logger.info(f"Successfully installed {installed_count} skills.")
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
        "--skills", help="Comma-separated list of skill names to install (default: all)"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing skills"
    )

    args = parser.parse_args()

    if args.path:
        target = Path(args.path).expanduser()
    elif args.tool:
        target = TOOL_PATHS.get(args.tool.lower())
        if not target:
            # Fallback to treating tool as a path if not found in TOOL_PATHS
            target = Path(args.tool).expanduser()
    else:
        print("Error: Either --tool or --path must be specified.", file=sys.stderr)
        sys.exit(1)

    skill_names = args.skills.split(",") if args.skills else None

    install_skills(target, skill_names, args.force)


if __name__ == "__main__":
    main()
