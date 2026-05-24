#!/usr/bin/env python3
"""WS6: Standardize environment variables in auth.py files.

Adds backward-compatible fallbacks so both old and new names work,
but the new standard name is checked first.

Standard: {SERVICE}_URL, {SERVICE}_TOKEN, {SERVICE}_SSL_VERIFY
"""

import re
from pathlib import Path

AGENTS_DIR = Path("/home/apps/workspace/agent-packages/agents")

# Map: (project, old_env_var) -> new_env_var
# Only change vars that deviate from the standard
MIGRATIONS = {
    # _AGENT_VERIFY -> _SSL_VERIFY
    "atlassian-agent": [
        ("ATLASSIAN_AGENT_VERIFY", "ATLASSIAN_SSL_VERIFY"),
    ],
    "data-science-mcp": [
        ("DATA_SCIENCE_MCP_VERIFY", "DATA_SCIENCE_MCP_SSL_VERIFY"),
    ],
    "github-agent": [
        ("GITHUB_VERIFY", "GITHUB_SSL_VERIFY"),
    ],
    "home-assistant-agent": [
        ("HOME_ASSISTANT_AGENT_VERIFY", "HOME_ASSISTANT_SSL_VERIFY"),
    ],
    "postiz-agent": [
        ("POSTIZ_AGENT_VERIFY", "POSTIZ_SSL_VERIFY"),
    ],
    "qbittorrent-agent": [
        ("QBITTORRENT_AGENT_VERIFY", "QBITTORRENT_SSL_VERIFY"),
    ],
    "stirlingpdf-agent": [
        ("STIRLINGPDF_AGENT_VERIFY", "STIRLINGPDF_SSL_VERIFY"),
        ("STIRLINGPDF_API_KEY", "STIRLINGPDF_TOKEN"),
    ],
    "wger-agent": [
        ("WGER_VERIFY", "WGER_SSL_VERIFY"),
        ("WGER_INSTANCE", "WGER_URL"),
        ("WGER_ACCESS_TOKEN", "WGER_TOKEN"),
    ],
    # _BASE_URL -> _URL (where there's a duplicate, keep only _URL)
    "adguard-home-agent": [
        ("ADGUARD_BASE_URL", "ADGUARD_URL"),
    ],
    "archivebox-api": [
        ("ARCHIVEBOX_BASE_URL", "ARCHIVEBOX_URL"),
        ("ARCHIVEBOX_API_KEY", "ARCHIVEBOX_TOKEN"),
    ],
    # _INSTANCE -> _URL
    "servicenow-api": [
        ("SERVICENOW_INSTANCE", "SERVICENOW_URL"),
    ],
    # LeanIX has complex auth - only fix the verify vars
    "leanix-agent": [
        ("SSL_VERIFY", "LEANIX_SSL_VERIFY"),
        ("LEANIX_AGENT_VERIFY", "LEANIX_SSL_VERIFY"),
        ("LEANIX_API_TOKEN", "LEANIX_TOKEN"),
    ],
}


def migrate_auth_file(project: str, migrations: list[tuple[str, str]]) -> int:
    """Apply backward-compatible env var migrations to auth.py."""
    pkg_name = project.replace("-", "_")
    auth_file = AGENTS_DIR / project / pkg_name / "auth.py"

    if not auth_file.exists():
        print(f"  ⚠️  {project}: auth.py not found")
        return 0

    content = auth_file.read_text()
    original = content
    changes = 0

    for old_var, new_var in migrations:
        if old_var not in content:
            continue

        # Pattern: os.getenv("OLD_VAR", default)
        # Replace with: os.getenv("NEW_VAR") or os.getenv("OLD_VAR", default)
        # This ensures backward compat while preferring the new name.

        # Handle: os.getenv("OLD_VAR", "default")
        pattern = rf'os\.getenv\("{re.escape(old_var)}"(,\s*"[^"]*")?\)'
        matches = list(re.finditer(pattern, content))

        if not matches:
            # Try with single quotes
            pattern = rf"os\.getenv\('{re.escape(old_var)}'(,\s*'[^']*')?\)"
            matches = list(re.finditer(pattern, content))

        for match in reversed(matches):  # reverse to preserve positions
            full_match = match.group(0)
            default_part = match.group(1)

            if default_part:
                # os.getenv("OLD", "default") -> os.getenv("NEW") or os.getenv("OLD", "default")
                replacement = f'os.getenv("{new_var}") or {full_match}'
            else:
                # os.getenv("OLD") -> os.getenv("NEW") or os.getenv("OLD")
                replacement = f'os.getenv("{new_var}") or os.getenv("{old_var}")'

            # Only replace if not already migrated (avoid double-wrapping)
            # Check if the new var is already referenced nearby
            start = max(0, match.start() - 50)
            context = content[start:match.end()]
            if new_var in context:
                continue

            content = content[:match.start()] + replacement + content[match.end():]
            changes += 1

    if changes > 0:
        auth_file.write_text(content)
        print(f"  ✅ {project}: {changes} env var(s) migrated")
    else:
        print(f"  ℹ️  {project}: no changes needed")

    return changes


def main():
    total_changes = 0
    for project, migrations in sorted(MIGRATIONS.items()):
        total_changes += migrate_auth_file(project, migrations)

    print(f"\n📊 Total: {total_changes} env var migrations applied")
    print("   All migrations are backward-compatible (old vars still work as fallback)")


if __name__ == "__main__":
    main()
