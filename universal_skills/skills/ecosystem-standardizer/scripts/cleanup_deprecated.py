#!/usr/bin/env python3
"""Remove deprecated files from all agent-packages projects.

Deprecated files:
- docs/legacy_readme.md (content migrated to README.md/overview.md)
- Any other files that shouldn't exist per the ecosystem standard
"""

import os
from pathlib import Path


def _agents_dir() -> Path:
    package_root = os.environ.get("AGENT_PACKAGES_ROOT")
    if package_root:
        return Path(package_root).expanduser().resolve() / "agents"
    workspace = Path(os.environ.get("AGENT_UTILITIES_WORKSPACE_ROOT", Path.cwd()))
    return workspace.expanduser().resolve() / "agent-packages" / "agents"


AGENTS_DIR = _agents_dir()

# Files that should NOT exist (relative to project root)
DEPRECATED_FILES = [
    "docs/legacy_readme.md",
]


def cleanup_project(project_dir: Path) -> list[str]:
    """Remove deprecated files from a project. Returns list of removed files."""
    removed = []
    for rel_path in DEPRECATED_FILES:
        f = project_dir / rel_path
        if f.exists():
            f.unlink()
            removed.append(rel_path)
    return removed


def main():
    total_removed = 0
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir() or agent_dir.name.startswith("."):
            continue
        removed = cleanup_project(agent_dir)
        if removed:
            for f in removed:
                print(f"  🗑️  {agent_dir.name}/{f}")
            total_removed += len(removed)

    if total_removed == 0:
        print("  ✅ No deprecated files found")
    print(f"\n📊 Removed {total_removed} deprecated file(s)")


if __name__ == "__main__":
    main()
