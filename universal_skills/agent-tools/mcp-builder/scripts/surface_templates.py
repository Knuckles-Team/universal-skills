"""Select documentation and packaging surfaces before formatting a scaffold.

MCP is required. The optional agent feature owns its extra, launch commands,
image stage and version metadata. Unknown template names pass through unchanged.
"""

import re


def _dockerfile(text: str, has_agent: bool) -> str:
    """Keep MCP as the final/default image even when an agent target exists."""
    text = text[text.index("FROM ") :]
    if has_agent:
        header = (
            "# MCP is the default image; use --target agent for the optional runtime.\n"
        )
        text = text.replace(
            "# Agent image (DEFAULT target); can also run the MCP server.",
            "# Optional agent image, selected explicitly with --target agent.",
        )
    else:
        header = (
            "# MCP serving image; --target mcp and the default target are equivalent.\n"
        )
        start = text.index("# Full agent runtime dependency closure.\n")
        end = text.index("FROM python:", start)
        text = text[:start] + text[end:]
        text = text.split("# Agent image (DEFAULT target)", 1)[0]
    return (
        "# syntax=docker/dockerfile:1\n"
        + header
        + text.rstrip()
        + "\n\nFROM mcp AS default\n"
    )


def _bumpversion(text: str, has_agent: bool) -> str:
    sections = re.split(r"(?m)(?=^\[bumpversion(?::|\]))", text)
    omitted = ["file:README.md"]  # README has no version marker.
    if not has_agent:
        omitted += ["file:a2a.json", "/agent_server.py"]
    return "".join(
        section
        for section in sections
        if not any(marker in section.partition("\n")[0] for marker in omitted)
    )


def _pyproject(text: str) -> str:
    text = text.replace('agent = [ "agent-utilities[agent-runtime]>=2.0.0,<3",]\n', "")
    return text.replace(' "agent-utilities[agent-runtime]>=2.0.0,<3",', "")


def _readme(text: str, has_agent: bool) -> str:
    text = text.replace(
        "error handling follow the `agent-utilities` conventions used by the fleet.",
        "error handling follow the `agent-connector-sdk` contracts.",
    )
    if has_agent:
        return text
    text = text.replace(
        "small Python client with governed MCP and A2A entry points where those surfaces are\n"
        "enabled.",
        "small Python client with a governed MCP entry point.",
    )
    text = text.replace('"{package_name}[all]"', '"{package_name}[mcp]"')
    text = text.replace("\n{agent_cmd}\n", "\n")
    text = text.replace('uvx --from "{package_name}[agent]" {agent_cmd}\n', "")
    text = text.replace(
        "client or agent → MCP/A2A entry point", "client → MCP entry point"
    )
    return text.replace(
        "docker build --file docker/Dockerfile --target agent -t {package_name}:agent-local .\n", ""
    )


def _index(text: str, has_agent: bool) -> str:
    text = text.replace("for the agent-utilities ecosystem", "using the connector SDK")
    if has_agent:
        return text
    text = text.replace("**API + MCP Server + A2A Agent**", "**API + MCP Server**")
    return text.replace(
        "`{package_name}` wraps the target service with typed, deterministic MCP tools and an\n"
        "optional Pydantic-AI agent server.",
        "`{package_name}` wraps the target service with typed, deterministic MCP tools.",
    )


def _overview(text: str, has_agent: bool) -> str:
    text = text.replace(
        "> Built on [`agent-utilities`](https://github.com/Knuckles-Team/agent-utilities) — the unified AGI Harness.",
        "> Built on [`agent-connector-sdk`](https://github.com/Knuckles-Team/agent-connector-sdk).",
    )
    if has_agent:
        return text
    text = text.replace(
        "**Ecosystem Role**: MCP Server + A2A Agent", "**Ecosystem Role**: MCP Server"
    )
    text = text.replace(
        "- **A2A Agent Server**: a Pydantic-AI graph agent (console script `{agent_cmd}`)\n"
        "  that calls the MCP tool surface and exposes an AG-UI web interface.\n",
        "",
    )
    return text.replace(
        "| ECO-4.2 | A2A Network & Consensus | `agent-utilities` (inherited) |\n", ""
    )


def _installation(text: str, has_agent: bool) -> str:
    text = text.replace(
        "Current agent runtime + Logfire tracing", "Optional agent runtime"
    )
    if has_agent:
        return text
    text = text.replace(
        '| `agent` | `pip install "{package_name}[agent]"` | Optional agent runtime |\n',
        "",
    )
    return text.replace('pip install -e ".[all]"', 'pip install -e ".[mcp]"')


def _deployment(text: str, has_agent: bool) -> str:
    if has_agent:
        return text
    text = text.replace("For an enabled agent surface, select `--target agent`. ", "")
    text = text.replace(
        "> `{package_name}` ships both an **MCP server** (console script `{mcp_cmd}`) and an\n"
        "> **A2A agent server** (console script `{agent_cmd}`).",
        "> `{package_name}` ships an **MCP server** (console script `{mcp_cmd}`).",
    )
    text = text.replace(
        "docker compose -f docker/agent.compose.yml up -d    # MCP + agent\n", ""
    )
    return text.split("\n## Run the A2A agent server\n", 1)[0].rstrip() + "\n"


def _debug_dockerfile(text: str, has_agent: bool) -> str:
    if has_agent:
        return text
    text = text.replace(
        "# Compile and install package in-place. Dev image carries the FULL agent runtime\n"
        "# (.[agent], which includes .[mcp]) so it can run either server while debugging.",
        "# Install the local MCP package for debugging.",
    )
    return text.replace(".[agent]", ".[mcp]")


def _init(text: str) -> str:
    return text.replace('    "{pkg_dir}.agent_server": "agent",\n', "").replace(
        ', "_AGENT_AVAILABLE"', ""
    )


def select_template(name: str, template: str, has_agent: bool) -> str:
    """Select a named scaffold constant before its placeholders are formatted."""
    selectors = {
        "DOCKERFILE": _dockerfile,
        "DEBUG_DOCKERFILE": _debug_dockerfile,
        "BUMPVERSION_CFG": _bumpversion,
        "README_MD": _readme,
        "DOCS_INDEX_MD": _index,
        "DOCS_OVERVIEW_MD": _overview,
        "DOCS_INSTALLATION_MD": _installation,
        "DOCS_DEPLOYMENT_MD": _deployment,
    }
    if name in selectors:
        return selectors[name](template, has_agent)
    if not has_agent and name == "PYPROJECT_TOML":
        return _pyproject(template)
    if not has_agent and name == "INIT_PY":
        return _init(template)
    return template
