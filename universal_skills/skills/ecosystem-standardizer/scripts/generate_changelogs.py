#!/usr/bin/env python3
"""Generate CHANGELOG.md for projects missing one.

Creates CHANGELOG.md in Keep a Changelog format, populated from git log.
"""

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _agents_dir() -> Path:
    package_root = os.environ.get("AGENT_PACKAGES_ROOT")
    if package_root:
        return Path(package_root).expanduser().resolve() / "agents"
    workspace = Path(os.environ.get("AGENT_UTILITIES_WORKSPACE_ROOT", Path.cwd()))
    return workspace.expanduser().resolve() / "agent-packages" / "agents"


AGENTS_DIR = _agents_dir()


def get_latest_version(project_dir: Path) -> str:
    """Extract version from pyproject.toml."""
    toml_path = project_dir / "pyproject.toml"
    if not toml_path.exists():
        return "0.1.0"
    import tomllib

    data = tomllib.loads(toml_path.read_text())
    return data.get("project", {}).get("version", "0.1.0")


def get_git_log(project_dir: Path, max_entries: int = 20) -> list[str]:
    """Get recent git log entries for a project."""
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                f"--max-count={max_entries}",
                "--oneline",
                "--",
                str(project_dir),
            ],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=project_dir.parent.parent,
        )
        if result.returncode == 0:
            return [
                line.strip()
                for line in result.stdout.strip().splitlines()
                if line.strip()
            ]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []


def generate_changelog(project_dir: Path) -> bool:
    """Generate CHANGELOG.md for a project."""
    changelog = project_dir / "CHANGELOG.md"
    if changelog.exists():
        return False

    version = get_latest_version(project_dir)
    project_name = project_dir.name
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_entries = get_git_log(project_dir)

    content = f"""# Changelog

All notable changes to **{project_name}** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [{version}] - {today}

### Added
- Initial changelog creation
- Ecosystem standardization compliance

### Changed
"""
    # Add git log entries as "Changed" items
    for entry in log_entries[:10]:
        # Strip commit hash
        msg = entry.split(" ", 1)[1] if " " in entry else entry
        content += f"- {msg}\n"

    changelog.write_text(content)
    return True


def main():
    created = 0
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir() or agent_dir.name.startswith("."):
            continue
        if generate_changelog(agent_dir):
            print(f"  ✅ {agent_dir.name}: CHANGELOG.md created")
            created += 1

    print(f"\n📊 Created {created} CHANGELOG.md files")


if __name__ == "__main__":
    main()
