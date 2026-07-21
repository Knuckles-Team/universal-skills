#!/usr/bin/env python3
"""Generate docs/concepts.md for every agent-package project.

Assigns unique CONCEPT prefixes, creates concept registries, and
links back to agent-utilities via ECO-4.0 bridge.
"""

import re
import tomllib
from pathlib import Path

AGENTS_DIR = Path("agent-packages/agents")
UTILITIES_DIR = Path("agent-packages/agent-utilities")
TUI_DIR = Path("agent-packages/agent-terminal-ui")
WEBUI_DIR = Path("agent-packages/agent-webui")

# Unique prefix assignments for each project
PREFIX_MAP = {
    # Already assigned in existing docs
    "ansible-tower-mcp": "ANSIBLE",
    "jellyfin-mcp": "JELLYFIN",
    "postiz-agent": "PA",
    "repository-manager": "RM",
    "scholarx": "SX",
    "systems-manager": "SYS",
    "stirlingpdf-agent": "STIRLINGPDF",
    "uptime-kuma-agent": "UKA",
    "wger-agent": "WGER",
    # New assignments
    "archivebox-api": "ABOX",
    "arr-mcp": "ARR",
    "atlassian-agent": "ATL",
    "audio-transcriber": "AUDIO",
    "container-manager-mcp": "CMGR",
    "data-science-mcp": "DSCI",
    "documentdb-mcp": "DOCDB",
    "genius-agent": "GENIUS",
    "github-agent": "GH",
    "gitlab-api": "GL",
    "home-assistant-agent": "HASS",
    "langfuse-agent": "LF",
    "leanix-agent": "LIX",
    "listmonk-api": "LM",
    "mealie-mcp": "MEAL",
    "media-downloader": "MDLD",
    "microsoft-agent": "MSFT",
    "nextcloud-agent": "NC",
    "owncast-agent": "OC",
    "plane-agent": "PLANE",
    "portainer-agent": "PORT",
    "qbittorrent-agent": "QBT",
    "searxng-mcp": "SRX",
    "servicenow-api": "SNOW",
    "tunnel-manager": "TUN",
    "vector-mcp": "VEC",
    # Non-agent projects
    "agent-utilities": "AU",
    "agent-terminal-ui": "TUI",
    "agent-webui": "WEBUI",
}

# Tool tag descriptions derived from register_*_tools patterns
TOOL_DESCRIPTIONS = {
    "auth": "Authentication & Session Management",
    "system": "System Information & Health",
    "docker": "Docker Container Management",
    "edge": "Edge Computing & Deployment",
    "environment": "Environment Configuration",
    "kubernetes": "Kubernetes Orchestration",
    "registry": "Container Registry Management",
    "stack": "Stack Deployment & Management",
    "template": "Template Management",
    "user": "User & Identity Management",
    "search": "Search & Discovery",
    "storage": "Storage & Persistence",
    "discovery": "Resource Discovery",
    "monitors": "Monitor Configuration",
    "status": "Status & Health Checks",
    "recipes": "Recipe Management",
    "admin": "Administration",
    "groups": "Group Management",
    "files": "File Management",
    "calendar": "Calendar Management",
    "contacts": "Contact Management",
    "sharing": "Sharing & Collaboration",
    "mail": "Email & Messaging",
    "chat": "Chat & Messaging",
    "incidents": "Incident Management",
    "cmdb": "Configuration Management DB",
    "torrents": "Torrent Management",
    "posts": "Social Media Posts",
    "analytics": "Analytics & Reporting",
    "pdf": "PDF Processing",
    "collection_management": "Collection Management",
    "body": "Body Measurements",
    "exercise": "Exercise Library",
    "nutrition": "Nutrition Tracking",
    "workout": "Workout Logging",
    "routine": "Routine Management",
    "git_operations": "Git Operations",
    "workspace_management": "Workspace Management",
    "project_management": "Project Management",
}


def get_tool_tags(project_dir: Path, pkg_name: str) -> list[str]:
    """Extract tool tags from mcp_server.py."""
    mcp_file = project_dir / pkg_name / "mcp_server.py"
    if not mcp_file.exists():
        return []
    content = mcp_file.read_text()
    tags = re.findall(r"register_(\w+)_tools", content)
    return sorted(set(tags))


def get_version(project_dir: Path) -> str:
    """Get version from pyproject.toml."""
    toml_file = project_dir / "pyproject.toml"
    if not toml_file.exists():
        return "0.0.0"
    data = tomllib.loads(toml_file.read_text())
    return data.get("project", {}).get("version", "0.0.0")


def get_description(project_dir: Path) -> str:
    """Get description from pyproject.toml."""
    toml_file = project_dir / "pyproject.toml"
    if not toml_file.exists():
        return ""
    data = tomllib.loads(toml_file.read_text())
    return data.get("project", {}).get("description", "")


def generate_concepts_md(project_name: str, project_dir: Path, prefix: str) -> str:
    """Generate the concepts.md content for a project."""
    pkg_name = project_name.replace("-", "_")
    version = get_version(project_dir)
    description = get_description(project_dir)
    tags = get_tool_tags(project_dir, pkg_name)

    lines = [
        f"# Concept Registry — {project_name}",
        "",
        f"> **Prefix**: `CONCEPT:{prefix}-*`",
        f"> **Version**: {version}",
        "> **Bridge**: [`CONCEPT:ECO-4.0`](../../agent-utilities/docs/concepts.md) (Unified Toolkit Ingestion)",
        "",
        "---",
        "",
        "## Project-Specific Concepts",
        "",
        "| Concept ID | Name | Description |",
        "|------------|------|-------------|",
    ]

    # Generate concepts from tool tags
    concept_num = 1
    for tag in tags:
        desc = TOOL_DESCRIPTIONS.get(tag, tag.replace("_", " ").title() + " Operations")
        lines.append(
            f"| `CONCEPT:{prefix}-{concept_num:03d}` | {desc} | "
            f"MCP tool domain `{tag}` — Action-routed dynamic tool registration |"
        )
        concept_num += 1

    # If no tool tags, add at least baseline concepts
    if not tags:
        lines.append(
            f"| `CONCEPT:{prefix}-001` | Core API Client | "
            f"Primary API client for {description or project_name} |"
        )
        lines.append(
            f"| `CONCEPT:{prefix}-002` | MCP Server | "
            f"Model Context Protocol server entry point |"
        )
        lines.append(
            f"| `CONCEPT:{prefix}-003` | A2A Agent | Agent-to-Agent protocol server |"
        )

    lines.extend(
        [
            "",
            "## Cross-Project References (from agent-utilities)",
            "",
            "| Concept ID | Name | Origin |",
            "|------------|------|--------|",
            "| `CONCEPT:ECO-4.0` | Unified Toolkit Ingestion | agent-utilities |",
            "| `CONCEPT:ORCH-1.2` | Confidence-Gated Router | agent-utilities |",
            "| `CONCEPT:OS-5.1` | Prompt Injection Defense | agent-utilities |",
            "| `CONCEPT:OS-5.2` | Cognitive Scheduler | agent-utilities |",
            "| `CONCEPT:AU-OS.governance.reactive-multi-axis-budget` | Guardrail Engine | agent-utilities |",
            "| `CONCEPT:AU-OS.governance.wasm-micro-agent-sandbox` | Audit Logging | agent-utilities |",
            "| `CONCEPT:KG-2.0` | Knowledge Graph Core | agent-utilities |",
            "",
            "## Synergy with agent-utilities",
            "",
            f"This project integrates with `agent-utilities` via `CONCEPT:ECO-4.0` (Unified Toolkit Ingestion). "
            f"The `{pkg_name}` MCP server registers its tools with the agent-utilities FastMCP middleware, "
            f"enabling automatic discovery, telemetry, and Knowledge Graph ingestion of all {prefix}-* concepts.",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    created = 0
    # Process agents
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir() or agent_dir.name.startswith("."):
            continue
        prefix = PREFIX_MAP.get(agent_dir.name)
        if not prefix:
            print(f"SKIP: No prefix for {agent_dir.name}")
            continue

        docs_dir = agent_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        concepts_file = docs_dir / "concepts.md"
        content = generate_concepts_md(agent_dir.name, agent_dir, prefix)
        concepts_file.write_text(content)
        created += 1
        print(f"  ✅ {agent_dir.name} → CONCEPT:{prefix}-*")

    # Process non-agent projects
    for proj_dir, name in [
        (TUI_DIR, "agent-terminal-ui"),
        (WEBUI_DIR, "agent-webui"),
    ]:
        if not proj_dir.exists():
            continue
        prefix = PREFIX_MAP[name]
        docs_dir = proj_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        content = generate_concepts_md(name, proj_dir, prefix)
        (docs_dir / "concepts.md").write_text(content)
        created += 1
        print(f"  ✅ {name} → CONCEPT:{prefix}-*")

    print(f"\n📊 Created {created} concepts.md files")
    print("📋 Prefix collision check:")
    prefixes = list(PREFIX_MAP.values())
    dupes = [p for p in prefixes if prefixes.count(p) > 1]
    if dupes:
        print(f"  ❌ COLLISIONS: {set(dupes)}")
    else:
        print(f"  ✅ No collisions across {len(prefixes)} prefixes")


if __name__ == "__main__":
    main()
