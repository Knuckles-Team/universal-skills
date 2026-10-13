#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Package Builder — Scaffolds a complete agent-package project.

Generates the full project structure following the configured golden standard,
including the modular api/ and mcp/ split, the shared pre-commit gates, release and Pages workflows, and a Material docs site,
AGENTS.md+CLAUDE.md
stub pattern, and the a2a.json / opencode.json / pytest.ini / MANIFEST.in /
.codespellignore / .vulture_ignore config set.

The generated quality surface also carries a pinned, host-provisioned scanner
profile consumed from the shared pipelines hooks; scanner implementation and
provisioning policy remain owned by pipelines.

See PARITY_MANIFEST.md (sibling of SKILL.md) for the definitive checklist.
"""

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from surface_templates import select_template
from backend_surfaces import select_backend_template
from cli_templates import CLI_PY, CLI_MCP_SYSTEM_PY, TESTS_CLI
from scaffold_dates import generation_date
from docs_assets import staged_theme_files, check_shared_theme, validate_theme_destinations
from spec_templates import render_spec_files
from quality_templates import (
    PRECOMMIT_CONFIG,
    SCANNER_CI_YML,
    PIPELINE_YML,
    PAGES_YML,
    SPEC_DASHBOARD_CONFIG,
    SPEC_DELIVERY_MD,
)
from transport_templates import AUTH_PY, API_CLIENT_BASE, TESTS_AUTH, TESTS_API_WRAPPER
from connector_templates import (
    render_kg_ingest,
    render_kg_ingest_test,
    render_connector_manifest,
    render_empty_fingerprints,
    render_schema_generator,
)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

# ── Utility ──────────────────────────────────────────────────────────────────


def to_pkg_dir(name: str) -> str:
    """Convert kebab-case package name to underscore Python package dir."""
    return name.replace("-", "_")


def to_display(name: str) -> str:
    """Convert kebab-case to Title Case display name."""
    return " ".join(w.capitalize() for w in name.split("-"))


def to_upper_env(name: str) -> str:
    """Convert kebab-case to UPPER_SNAKE env prefix."""
    return name.replace("-", "_").upper()


GITHUB_BADGE_URLS = (
    ("GitHub Repo stars", "https://img.shields.io/github/stars/{repository}"),
    ("GitHub forks", "https://img.shields.io/github/forks/{repository}"),
    ("GitHub contributors", "https://img.shields.io/github/contributors/{repository}"),
    ("GitHub license", "https://img.shields.io/github/license/{repository}"),
    (
        "GitHub last commit (by committer)",
        "https://img.shields.io/github/last-commit/{repository}",
    ),
    ("GitHub pull requests", "https://img.shields.io/github/issues-pr/{repository}"),
    (
        "GitHub closed pull requests",
        "https://img.shields.io/github/issues-pr-closed/{repository}",
    ),
    ("GitHub issues", "https://img.shields.io/github/issues/{repository}"),
    ("GitHub top language", "https://img.shields.io/github/languages/top/{repository}"),
    (
        "GitHub language count",
        "https://img.shields.io/github/languages/count/{repository}",
    ),
    ("GitHub repo size", "https://img.shields.io/github/repo-size/{repository}"),
    (
        "GitHub repo file count (file type)",
        "https://img.shields.io/github/directory-file-count/{repository}",
    ),
)
PYPI_BADGE_URLS = (
    ("PyPI - Version", "https://img.shields.io/pypi/v/{distribution}"),
    ("PyPI - Downloads", "https://img.shields.io/pypi/dd/{distribution}"),
    ("PyPI - License", "https://img.shields.io/pypi/l/{distribution}"),
    ("PyPI - Wheel", "https://img.shields.io/pypi/wheel/{distribution}"),
    (
        "PyPI - Implementation",
        "https://img.shields.io/pypi/implementation/{distribution}",
    ),
)


def render_public_badges(package_name: str, *, mcp_server: bool) -> str:
    """Render the canonical offline public-surface badge set."""
    repository = f"Knuckles-Team/{package_name}"
    values = {"repository": repository, "distribution": package_name}
    definitions = [*GITHUB_BADGE_URLS, *PYPI_BADGE_URLS]
    if mcp_server:
        definitions.append(("MCP Server", "https://badge.mcpx.dev?type=server"))
    lines = []
    for alt, url in definitions:
        title = " 'MCP Server'" if alt == "MCP Server" else ""
        lines.append(f"![{alt}]({url.format(**values)}{title})")
    return "\n".join(lines)


def _write_generated_text(path: Path, content: str) -> bool:
    """Create a generated text file without overwriting an existing file.

    A scaffold may be re-run in a checkout that already contains operator or
    project-owned files.  Matching content is already in the desired state;
    different content is deliberately preserved so a generator update cannot
    destroy local work.  The return value tells the caller whether a file was
    created.
    """

    if path.exists() or path.is_symlink():
        if path.is_file() and not path.is_symlink():
            try:
                identical = path.read_text(encoding="utf-8") == content
            except (OSError, UnicodeError):
                identical = False
            state = "already current" if identical else "preserved existing"
        else:
            state = "preserved existing non-file"
        print(f"  ↷ {path} ({state})")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def _copy_generated_file(path: Path, destination: Path) -> bool:
    """Copy a bundled artifact only when its destination does not exist."""

    if destination.exists() or destination.is_symlink():
        if destination.is_file() and not destination.is_symlink():
            try:
                identical = destination.read_bytes() == path.read_bytes()
            except OSError:
                identical = False
            state = "already current" if identical else "preserved existing"
        else:
            state = "preserved existing non-file"
        print(f"  ↷ {destination} ({state})")
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, destination)
    return True


# ── Templates (SDK and shared pipelines contracts) ──────────────────────────────────
# Templates are stored as (text, needs_format) pairs in the files map below.
# needs_format=False templates are written verbatim (they contain literal
# braces that str.format would mangle).

PYPROJECT_TOML = """\
[build-system]
requires = [ "setuptools>=80.9.0", "wheel",]
build-backend = "setuptools.build_meta"

[project]
name = "{package_name}"
version = "0.1.0"
description = "{description}"
readme = "README.md"
classifiers = [ "Development Status :: 4 - Beta", "License :: OSI Approved :: MIT License", "Environment :: Console", "Operating System :: POSIX :: Linux", "Programming Language :: Python :: 3",]
requires-python = ">=3.12, <3.15"
dependencies = [
    "agent-connector-sdk>=0.1.0,<1",{gql_core_dep}
]
[[project.authors]]
name = "Repository Maintainers"

[project.license]
text = "MIT"

[project.optional-dependencies]
mcp = [ "agent-connector-sdk>=0.1.0,<1",]
agent = [ "agent-utilities[agent-runtime]>=2.0.0,<3",]
{gql_extra}all = [
    "agent-connector-sdk>=0.1.0,<1", "agent-utilities[agent-runtime]>=2.0.0,<3",{gql_all_dep}
]
test = [
    "pytest-xdist>=3.6.0", "pytest", "pytest-asyncio", "pytest-cov",]

[project.scripts]
{mcp_cmd} = "{pkg_dir}.mcp_server:mcp_server"
{agent_entry}

# Fleet contribution (CONCEPT:OS-5.52 / AU-KG.ontology.federation-provider-leg): advertise this
# package's skills, prompts, OWL/RDF ontology, and source-connector presets so
# agent-utilities discovers + federates them without importing this package's agent code.
[project.entry-points."agent_utilities.skill_providers"]
{package_name} = "{pkg_dir}.skills"

[project.entry-points."agent_utilities.prompt_providers"]
{package_name} = "{pkg_dir}.prompts"

[project.entry-points."agent_utilities.ontology_providers"]
{package_name} = "{pkg_dir}.ontology"

[project.entry-points."agent_utilities.source_connector_providers"]
{package_name} = "{pkg_dir}.connectors"

[tool.uv.workspace]
members = ["."]

[tool.setuptools]
include-package-data = true

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint.isort]
known-first-party = ["{pkg_dir}"]

[tool.mypy]
python_version = "3.12"
ignore_missing_imports = true
check_untyped_defs = true

# Shared public documentation contract. The hook authority is declared in
# .pre-commit-config.yaml; these values identify this generated repository and
# keep its README/AGENTS surface deterministic without network access.
[tool.pipelines_hooks]
packages = ["{pkg_dir}"]

[tool.pipelines_hooks.stdout_writes]
served_paths = ["{pkg_dir}"]

[tool.pipelines_hooks.public_surface]
repository = "Knuckles-Team/{package_name}"
distribution = "{package_name}"
pages_url = "https://knuckles-team.github.io/{package_name}/"
mcp_server = {mcp_server}

[dependency-groups]
dev = [
    "pytest-timeout>=2.4.0",
]

[tool.setuptools.package-data]
{pkg_dir} = [ "mcp_config.json", "prompts/**", "skills/**", "ontology/**", "connectors/**", "connector_manifest.yml",]

[tool.ruff.lint]
select = [ "E", "F", "I", "UP", "B",]
ignore = [ "E402", "E501", "B008",]

[tool.setuptools.packages.find]
where = [ ".",]
include = ["{pkg_dir}*"]

[tool.vulture]
ignore_names = ["request", "config"]
"""

BUMPVERSION_CFG = """\
[bumpversion]
current_version = 0.1.0
commit = True
tag = True

[bumpversion:file:pyproject.toml]
search = version = "{{current_version}}"
replace = version = "{{new_version}}"

[bumpversion:file:a2a.json]
search = "version": "{{current_version}}"
replace = "version": "{{new_version}}"

[bumpversion:file:README.md]
search = Version: {{current_version}}
replace = Version: {{new_version}}

[bumpversion:file:{pkg_dir}/agent_server.py]
search = __version__ = "{{current_version}}"
replace = __version__ = "{{new_version}}"

[bumpversion:file:{pkg_dir}/mcp_server.py]
search = __version__ = "{{current_version}}"
replace = __version__ = "{{new_version}}"
"""

# Verbatim golden gitlab-api pre-commit gate (no format placeholders — the
# bash one-liners contain literal braces).

# Scanner policy files are intentionally separate from the pre-commit YAML:
# KISS owns its own TOML grammar, CCCC's caps are human-readable, and
# import-linter's contracts should be reviewable without decoding a Python
# string.  Tool versions live in [tool.agent_utilities.scanners] in
# PYPROJECT_TOML; these files contain thresholds/contracts only.


DOCKERFILE = """\
# syntax=docker/dockerfile:1
# Two runtime images from ONE Dockerfile, selected by build --target. Both are
# multi-stage builds that ship only the installed runtime:
#
#   --target agent  (DEFAULT)  installs {package_name}[agent] = the agent runtime
#                              (agent-utilities[agent-runtime,logfire]: engine + agent +
#                              skills). Because [agent] also includes [mcp], this image
#                              can run either the agent or the MCP server. Publish and
#                              deploy it by immutable manifest digest.
#
#   --target mcp               installs {package_name}[mcp] = the MCP serving runtime.
#                              The SDK graph client engine remains present;
#                              only the optional agent orchestration stack is omitted.
#
#   docker build --file docker/Dockerfile --target agent -t {package_name}:local .
#   docker build --file docker/Dockerfile --target mcp -t {package_name}:mcp .
# Build from the repository root with --file docker/Dockerfile.
FROM python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de AS builder-base
COPY --from=ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \\
    UV_LINK_MODE=copy \\
    UV_SYSTEM_PYTHON=1 \\
    UV_HTTP_TIMEOUT=3600
# A few transitive deps ship no manylinux wheel and build from sdist, needing a C++
# toolchain. Install it in the builder only — final stages copy just /usr/local.
RUN apt-get update \\
    && apt-get install -y --no-install-recommends build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Build the connector from this checkout, including generated runtime data.
# Copy only the package and its wheel metadata, not credentials or local tooling.
WORKDIR /src
COPY pyproject.toml README.md LICENSE ./
COPY {pkg_dir}/ ./{pkg_dir}/

# MCP serving dependency closure (including SDK graph client).
FROM builder-base AS builder-mcp
RUN --mount=type=cache,target=/root/.cache/uv \\
    uv pip install --system --break-system-packages --prerelease=allow ".[mcp]"

# Full agent runtime dependency closure.
FROM builder-base AS builder-agent
RUN --mount=type=cache,target=/root/.cache/uv \\
    uv pip install --system --break-system-packages --prerelease=allow ".[agent]"

FROM python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de AS runtime-base
ARG HOST=127.0.0.1
ARG PORT=8000
ARG TRANSPORT="stdio"
ARG AUTH_TYPE="none"
ENV HOST=${{HOST}} \\
    PORT=${{PORT}} \\
    TRANSPORT=${{TRANSPORT}} \\
    AUTH_TYPE=${{AUTH_TYPE}} \\
    PYTHONUNBUFFERED=1 \\
    PATH="/root/.local/bin:/usr/local/bin:${{PATH}}" \\
    UV_HTTP_TIMEOUT=3600 \\
    UV_SYSTEM_PYTHON=1 \\
    UV_COMPILE_BYTECODE=1 \\
    UV_LINK_MODE=copy

# MCP serving image.
FROM runtime-base AS mcp
COPY --from=builder-mcp /usr/local /usr/local
CMD ["{mcp_cmd}"]

# Agent image (DEFAULT target); can also run the MCP server.
FROM runtime-base AS agent
COPY --from=builder-agent /usr/local /usr/local
CMD ["{agent_cmd}"]
"""

DEBUG_DOCKERFILE = """\
FROM python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de
COPY --from=ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a /uv /uvx /bin/

ARG HOST=127.0.0.1
ARG PORT=8000
ARG TRANSPORT="stdio"
ARG AUTH_TYPE="none"

ENV HOST=${{HOST}} \\
    PORT=${{PORT}} \\
    TRANSPORT=${{TRANSPORT}} \\
    AUTH_TYPE=${{AUTH_TYPE}} \\
    PYTHONUNBUFFERED=1 \\
    PATH="/usr/local/cargo/bin:/root/.local/bin:/usr/local/bin:${{PATH}}" \\
    UV_HTTP_TIMEOUT=3600 \\
    UV_SYSTEM_PYTHON=1 \\
    UV_COMPILE_BYTECODE=1

# Install bounded development dependencies from the base distribution.
RUN apt-get update \\
    && apt-get install -y --no-install-recommends default-jre ripgrep tree fd-find nano build-essential cmake libssl-dev libcurl4-openssl-dev pkg-config cargo rustc \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Compile and install package in-place. Dev image carries the FULL agent runtime
# (.[agent], which includes .[mcp]) so it can run either server while debugging.
RUN uv pip install --system --upgrade --verbose --no-cache --break-system-packages --prerelease=allow .[agent]

CMD ["{mcp_cmd}"]
"""

AGENT_COMPOSE_YML = """\
version: '3.8'

services:
  {package_name}-mcp:
    # MCP serving image (built with `--target mcp`).
    image: "${{MCP_IMAGE:?set-MCP_IMAGE-to-image@sha256-digest}}"
    container_name: {package_name}-mcp
    hostname: {package_name}-mcp
    restart: always
    volumes:
      - type: bind
        source: ${{CONNECTOR_CONFIG_DIR:?set-CONNECTOR_CONFIG_DIR-to-a-reference-only-config-directory}}
        target: /etc/connector
        read_only: true
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
      - AUTH_TYPE=${{AUTH_TYPE:?set-AUTH_TYPE-to-a-configured-auth-provider}}
      - CONNECTOR_CONFIG_FILE=/etc/connector/config.json
      - {upper_name}_ALLOW_PLAINTEXT=${{{upper_name}_ALLOW_PLAINTEXT:-false}}
    ports:
      - "127.0.0.1:8000:8000"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  {package_name}-agent:
    # Full agent runtime image. Deployment inputs must be immutable digests.
    image: "${{AGENT_IMAGE:?set-AGENT_IMAGE-to-image@sha256-digest}}"
    container_name: {package_name}-agent
    hostname: {package_name}-agent
    restart: always
    depends_on:
      - {package_name}-mcp
    volumes:
      - type: bind
        source: ${{CONNECTOR_CONFIG_DIR:?set-CONNECTOR_CONFIG_DIR-to-a-reference-only-config-directory}}
        target: /etc/connector
        read_only: true
    command: [ "{agent_cmd}" ]
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT={agent_port}
      - MCP_URL=http://{package_name}-mcp:8000/mcp
      - CONNECTOR_CONFIG_FILE=/etc/connector/config.json
      - {upper_name}_ALLOW_PLAINTEXT=${{{upper_name}_ALLOW_PLAINTEXT:-false}}
    ports:
      - "127.0.0.1:{agent_port}:{agent_port}"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:{agent_port}/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
"""

MCP_COMPOSE_YML = """\
version: '3.8'

services:
  {package_name}-mcp:
    # MCP serving image (built with `--target mcp`).
    image: "${{MCP_IMAGE:?set-MCP_IMAGE-to-image@sha256-digest}}"
    container_name: {package_name}-mcp
    hostname: {package_name}-mcp
    restart: always
    volumes:
      - type: bind
        source: ${{CONNECTOR_CONFIG_DIR:?set-CONNECTOR_CONFIG_DIR-to-a-reference-only-config-directory}}
        target: /etc/connector
        read_only: true
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
      - AUTH_TYPE=${{AUTH_TYPE:?set-AUTH_TYPE-to-a-configured-auth-provider}}
      - CONNECTOR_CONFIG_FILE=/etc/connector/config.json
      - {upper_name}_ALLOW_PLAINTEXT=${{{upper_name}_ALLOW_PLAINTEXT:-false}}
    ports:
      - "127.0.0.1:8000:8000"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
"""

STARSHIP_TOML = """\
"$schema" = "https://starship.rs/config-schema.json"

add_newline = true
command_timeout = 1000

format = \"\"\"\\
${{custom.shell}}\\
${{directory}}\\
${{git_branch}}${{git_status}}\\
${{line_break}}\\
${{character}}\"\"\"

right_format = \"\"\"${{nodejs}}${{time}}\"\"\"

# ── Left side ───────────────────────────────────────────────────────────────

# Shell name (blue diamond like your first segment)
[custom.shell]
command = \"\"\"echo ${{SHELL##*/}}\"\"\"
when = true
format = "[ ╭─](fg:#0077c2)[ $output ](fg:#ffffff bg:#0077c2)[ ](fg:#0077c2)"

# Directory (gray powerline)
[directory]
style = "fg:#E4E4E4 bg:#444444"
format = "[ $path ](fg:#E4E4E4 bg:#444444)[ ](fg:#444444)"
truncation_len = 0
truncate_to_repo = false
use_logical_path = false

# Git
[git_branch]
format = "[ ](fg:#FFFB38)[ $branch ](fg:#011627 bg:#FFFB38)"
style = "fg:#011627 bg:#FFFB38"

[git_status]
format = "[$all_status$ahead_behind ](fg:#011627 bg:#FFFB38)"
style = "fg:#011627 bg:#FFFB38"
ahead = "↑$count"
behind = "↓$count"
diverged = "↑$ahead_count↓$behind_count"
modified = "!"
staged = "+"
untracked = "?"
deleted = "✘"
renamed = "»"

# ── Right side ──────────────────────────────────────────────────────────────

# Node.js (green on dark)
[nodejs]
format = "[ ](fg:#303030)[  $version ](fg:#3C873A bg:#303030)[ ](fg:#303030)"
detect_files = ["package.json"]

# Time (cyan diamond)
[time]
disabled = false
format = "[ ](fg:#40c4ff)[  $time ](fg:#ffffff bg:#40c4ff)[ ](fg:#40c4ff)"
time_format = "%H:%M:%S"

# ── Bottom line ─────────────────────────────────────────────────────────────

[character]
success_symbol = "[╰─❯ ](fg:#e0f8ff)"
error_symbol = "[╰─❯ ](fg:#ef5350)"

# Python module (nice to have in a Python container)
[python]
format = "[  $version ](fg:#3776AB bg:#444444)[ ](fg:#444444)"
style = "fg:#3776AB bg:#444444"
"""

DOCKERIGNORE = """\
ollama/
venv/
__pycache__/
*.pyc
.git/
.env
scripts/
tests/
{pkg_dir}.egg-info*
models/
.github/
build/
.bumpversion.cfg
.pre-commit-config.yaml
pytest.ini
./tests/

Dockerfile
debug.Dockerfile
compose.yml
"""

ENV_EXAMPLE = """\
# Optional SDK settings, loaded by the operator; no credentials are stored here.
HOST=127.0.0.1
PORT=8000
TRANSPORT=stdio
AUTH_TYPE=none
SYSTEMTOOL=True
# Set {upper_name}_BASE_URL at runtime to the authorized service origin.
# Set {upper_name}_TOKEN_REF to an env:// or openbao:// credential reference.
# Opt in only for an explicitly authorized HTTP origin in {upper_name}_BASE_URL.
{upper_name}_ALLOW_PLAINTEXT=false
# Configure {upper_name}_TLS_PROFILE or {upper_name}_TLS_PROFILE_REF per SDK TLS policy.
# Network exposure/authentication and token exchange remain separately authorized.
"""

PYTEST_INI = """\
[pytest]
timeout = 60
asyncio_mode = auto
testpaths = tests
markers =
    integration: Integration tests
    concept(id): associate a test with a CONCEPT id
addopts = -m "not integration"
filterwarnings =
    ignore:.*exclude_args.*
"""

A2A_JSON = """\
{{
  "name": "{package_name}-agent",
  "type": "agent",
  "version": "0.1.0",
  "description": "{description}",
  "url": "https://github.com/Knuckles-Team/{package_name}/tree/main",
  "license": "MIT",
  "capabilities": [
    {{
      "id": "run_graph_flow",
      "name": "Graph Flow Execution",
      "description": "Execute a workflow through the agent's graph orchestration engine"
    }}
  ],
  "tools": [
    {{
      "id": "graph-flow",
      "type": "flow",
      "description": "Run complex multi-step workflows via Pydantic-Graph"
    }}
  ]
}}
"""

OPENCODE_JSON = """\
{
  "$schema": "https://opencode.ai/config.json"
}
"""

CODESPELLIGNORE = """\
# codespell ignore words list
linar
nam
tread
ot
ans
uv
mcp
pydantic
logfire
langfuse
fastmcp
eunomia
agentic
pre-commit
setuptools
pyproject
bumpversion
"""

VULTURE_IGNORE = """\
DEFAULT_AGENT_DESCRIPTION
DEFAULT_AGENT_SYSTEM_PROMPT
health_check
get_client
"""

CLAUDE_MD = """\
# CLAUDE.md

Guidance for Claude Code (claude.ai/code) when working in this repository.

To prevent drift, the **canonical agent guidance lives in `AGENTS.md`** and is
imported below, so `CLAUDE.md` and `AGENTS.md` always stay in sync. Edit
`AGENTS.md` for any change — never edit the body of this file.

@AGENTS.md
"""

LICENSE_MIT = """\
MIT License

Copyright (c) {year} Repository Maintainers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

MANIFEST_IN = """\
include LICENSE
include README.md
include requirements.txt
# Scanner policies and wrappers are included in source distributions so a
# checkout recreated from the sdist has the same reviewed quality surface.
# They remain source-checkout tooling, not runtime wheel/package data; hooks
# never install these native tools and the Docker runtime excludes scripts/.
include .pre-commit-config.yaml
graft .github/workflows
graft scripts
graft tests
graft docs
graft specs
graft .pipeline-theme
graft docker
include mkdocs.yml pytest.ini .bumpversion.cfg
include .config/spec-dashboard.json
global-exclude __pycache__ *.py[cod]
recursive-include {pkg_dir} *.py *.json *.md *.yaml *.yml
"""

GITIGNORE = """\
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[codz]
*$py.class

/.ruff_cache/
/.ci/
/mcp/
# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py.cover
.hypothesis/
.pytest_cache/
cover/

# Environments
.env
.envrc
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Ruff stuff:
.ruff_cache/

# PyPI configuration file
.pypirc

# Scratch / debug files at root (keep the repo root pristine)
/test_*.py
/fix_*.py
/debug_*.py
/scratch_*.py
/temp_*.py

# Transient logs, traces, patch files, and test outputs
*.orig
*.rej
*.patch
*.log
*output*.txt
*errors*.txt
failed_tests.txt
trace.txt

# Structural scanner runtime state.  The threshold/config files under
# `.kiss/` are generated and tracked; only kiss's unsafe auto-config and
# transient reports are ignored.  Hooks refuse `.kissconfig` instead of
# silently accepting its calibrated defaults.
.kissconfig
.kiss/*.json
.jscpd-report/

# P0.2 (graph-os-completion-program): materialized, dev-machine-only symlink to
# the real agent-utilities checkout, used so this package resolves standalone
# against its own tracked lock instead of the outer ecosystem workspace. Never
# tracked.
.uv-workspace-siblings/
"""

GITATTRIBUTES = """\
# Auto detect
*                 text=auto

# Source code
*.bash            text eol=lf
*.bat             text eol=crlf
*.cmd             text eol=crlf
*.css             text diff=css
*.htm             text diff=html
*.html            text diff=html
*.ini             text
*.js              text
*.json            text
*.jsx             text
*.ps1             text eol=crlf
*.py              text diff=python
*.sh              text eol=lf
*.sql             text
*.ts              text
*.tsx             text
*.xml             text

# Docker
Dockerfile        text

# Documentation
*.ipynb           text
*.markdown        text diff=markdown eol=lf
*.md              text diff=markdown eol=lf
*.txt             text
AUTHORS           text
CHANGELOG         text
LICENSE           text
*README*          text
"""

README_MD = """\
# {display_name}

{badge_lines}

{description}

The [documentation site](https://knuckles-team.github.io/{package_name}/) contains the
full API, deployment, security, and operational reference. This README is the concise
entry point for installation and the supported runtime surfaces.

## Overview

`{package_name}` is a typed provider package for the agent ecosystem. It combines a
small Python client with governed MCP and A2A entry points where those surfaces are
enabled. Configuration uses runtime credential references; resolved credentials and
private endpoints are never committed.

## Key capabilities

- **Typed boundaries** — Pydantic request and response models keep provider data
  explicit and validate it before it reaches an agent or graph.
- **One package, shared policy** — authentication, telemetry, action routing, and
  error handling follow the `agent-utilities` conventions used by the fleet.
- **Graph-ready content** — skills, prompts, ontology, and connector presets are
  packaged as discoverable data for the epistemic graph.
- **Operational safety** — TLS profiles, bounded responses, loopback defaults, and
  immutable container references are part of the generated deployment contract.

## Quick start

Install the package and run its generated entry points:

```bash
python -m pip install "{package_name}[all]"
{mcp_cmd}
{agent_cmd}
```

For an on-demand run, use `uvx`:

```bash
uvx --from "{package_name}[mcp]" {mcp_cmd}
uvx --from "{package_name}[agent]" {agent_cmd}
```

The networked server binds to loopback by default:

```bash
{mcp_cmd} --transport streamable-http --host 127.0.0.1 --port 8000
```

## Architecture

The provider keeps the boundary between transport and domain code explicit:

```text
client or agent → MCP/A2A entry point → typed tool module → API client → provider
                                  └── skills, prompts, ontology, connector presets
```

The MCP surface uses action-routed tools. Pass an `action` and a JSON `params_json`
payload. Regenerate `schemas/mcp_tools.json` with `python scripts/generate_tool_schemas.py`
after changing a tool contract, and keep the examples below aligned with that schema.

<!-- MCP-TOOLS-TABLE:START -->
<!-- MCP-TOOLS-TABLE:END -->

## MCP configuration

The server supports local `stdio` and authenticated `streamable-http` deployments.
Keep endpoint, credential, selector, and TLS references in SDK configuration; do not put
resolved values in client configuration.

```json
{{
  "mcpServers": {{
    "{mcp_cmd}": {{
      "command": "{mcp_cmd}",
      "args": [],
      "env": {{"SYSTEMTOOL": "true"}}
    }}
  }}
}}
```

For a networked deployment, use an authenticated TLS ingress and keep the allowlist in
`MCP_ALLOWED_HOSTS`. A configured remote example is `https://service.example.invalid/mcp`;
it is documentation-only and is never contacted by the generator.

<!-- MCP-CONFIG-EXAMPLES:START -->

```json
{{
  "mcpServers": {{
    "{mcp_cmd}": {{
      "command": "{mcp_cmd}",
      "args": ["--transport", "streamable-http", "--port", "8000"],
      "env": {{
        "TRANSPORT": "streamable-http",
        "HOST": "127.0.0.1",
        "PORT": "8000",
        "SYSTEMTOOL": "true"
      }}
    }}
  }}
}}
```

<!-- MCP-CONFIG-EXAMPLES:END -->

Container builds install this checkout, so the connector need not be published first.
Run from the repository root:

```bash
docker build --file docker/Dockerfile --target mcp -t {package_name}:mcp-local .
docker build --file docker/Dockerfile --target agent -t {package_name}:agent-local .
```

Deploy reviewed images by digest (`{package_name}@sha256:<digest>`) and include
`--cap-drop=ALL` in the runtime policy. The [deployment guide](https://knuckles-team.github.io/{package_name}/deployment/)
contains the complete transport and container examples.

## Documentation

Use the [Pages documentation](https://knuckles-team.github.io/{package_name}/) for
installation details, API capabilities, deployment profiles, platform integration,
and the concept registry. The concise local references remain available at:

- [Installation](docs/installation.md)
- [Usage](docs/usage.md)
- [Deployment](docs/deployment.md)
- [Platform](docs/platform.md)
- [Concept registry](docs/concepts.md)

## Development

Create an isolated branch, install the test extra, and run the complete local gate:

```bash
uv sync --extra test
pytest tests -q
pre-commit run --all-files
```

Keep MCP examples and environment documentation aligned with the implemented settings.
Add focused positive and adversarial tests for every behavior change. See
`AGENTS.md` for the current module ownership and release checks.

## License

This project is distributed under the MIT license. See [LICENSE](LICENSE) for the
complete terms.
"""

CHANGELOG_MD = """\
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Scaffold generated: {date}. This is not a release or delivery date.

### Added
- Initial scaffold; release and delivery remain unclaimed.
- Modular subfolders for API wrappers (`api/`) and action-routed MCP tools (`mcp/`).
- Material-theme mkdocs documentation site (7 standard pages).
- Full pre-commit quality gate and flat `tests/` structure.
"""

# ── GitHub workflows (golden verbatim) ───────────────────────────────────────


# Structural scanners run in a dedicated source-checkout workflow.  Keeping
# provisioning here, rather than in a pre-commit hook or a runtime package,
# makes the no-download hook contract explicit while ensuring every generated
# project has a reproducible CI census.  The profile assertion intentionally
# duplicates the checked-in versions: if either side drifts, CI fails before a
# scanner can report a result under the wrong toolchain.


# 2026-08-13 Windows-coverage program: pipeline.yml/pages.yml never ran a
# single test on this package -- pipeline.yml only builds/publishes via a
# self-hosted runner, pages.yml only builds docs. This is the first workflow
# scaffolded packages get that actually imports and exercises the code, on
# BOTH platforms it runs on (ubuntu here for a real green baseline, windows
# for the coverage this whole file exists to add). Report-only
# (continue-on-error everywhere) so it never blocks the publish pipeline.
WINDOWS_CI_YML = """\
name: Cross-platform coverage

# Report-only (continue-on-error on every step) -- does not touch
# pipeline.yml/pages.yml. scripts/check_import_safety.py auto-detects this
# package's import name from pyproject.toml's [project].name, so this file
# needs no per-package templating. See that script's own docstring for
# exactly what --simulate-windows does and does not model, and its
# sys.platform-guard false-positive limitation -- if this package
# legitimately guards a POSIX-only import behind
# `sys.platform == "win32"`, add `--exclude <dotted.module.name>` to BOTH
# this file's windows job below and .pre-commit-config.yaml's
# check-import-safety hook.

on:
  pull_request:
    paths:
      - '{pkg_dir}/**'
      - 'scripts/**'
      - 'tests/**'
      - 'pyproject.toml'
      - 'uv.lock'
      - '.github/workflows/windows-ci.yml'
  push:
    branches:
      - 'main'

permissions:
  contents: read

jobs:
  windows:
    name: Windows coverage (report only, never blocks)
    runs-on: windows-latest
    permissions:
      contents: read
    defaults:
      run:
        shell: bash
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
        with:
          persist-credentials: false

      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5
        with:
          python-version: '3.12'

      - uses: astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e # v6
        with:
          version: '0.11.7'
          enable-cache: true
          cache-dependency-glob: uv.lock

      - name: Sync test environment
        id: sync
        continue-on-error: true
        run: |
          uv sync --extra test
          echo "$PWD/.venv/Scripts" >> "$GITHUB_PATH"
          echo "$PWD/.venv/bin" >> "$GITHUB_PATH"

      - name: Cross-platform import safety (real Windows interpreter)
        if: steps.sync.outcome == 'success'
        continue-on-error: true
        run: python3 scripts/check_import_safety.py

      - name: Unit tests
        if: steps.sync.outcome == 'success'
        continue-on-error: true
        run: python3 -m pytest tests -q --tb=short --timeout=120

      - name: Windows coverage summary
        if: always()
        run: |
          echo "## Windows coverage ran in report-only mode" >> "$GITHUB_STEP_SUMMARY"
          echo "Both steps above use continue-on-error: true -- a red step" >> "$GITHUB_STEP_SUMMARY"
          echo "here is a real Windows regression and never blocks the" >> "$GITHUB_STEP_SUMMARY"
          echo "publish pipeline." >> "$GITHUB_STEP_SUMMARY"
"""

# ── AGENTS.md (golden pattern, incl. Quality Bar + worktree sections) ─────────

ROOT_AGENTS_MD = """\
# {display_name} engineering contract

## Architecture

`{pkg_dir}/api/` owns service operations; `mcp/` adapts them to tools.
The connector SDK owns HTTP, credential references, TLS, server policy,
registration, content publication and ingestion transport. The graph engine
owns durable storage and semantics. Optional orchestration belongs to
agent-utilities and must not become an MCP dependency.

## Setup and commands

Use the repository's locked environment. Install its declared test dependencies
and pre-commit before running `pre-commit run --all-files` and `pytest -q`.
The shared pipelines hooks own scanner versions and gate policy; provision
those tools through the approved development environment, never a hook-time
installer. Generate schemas with `python scripts/generate_tool_schemas.py`,
then check them with `--check`. Run `mkdocs build --strict` for documentation.

## Development rules

Keep configuration as operator-provided references. Do not generate credentials,
commit resolved secrets, bypass failing gates, or infer publication/deployment
permission from a scaffolding request. Test real contract behavior with fakes
at outbound boundaries. A schema fingerprint is not release certification.

## Documentation and delivery

[README.md](README.md) contains install/start instructions; [docs/](docs/index.md)
contains usage and constraints. Keep both synchronized with code and examples.
Follow the current shared pipelines spec standard for requirement bundles and
its generators for status and the delivery dashboard; do not hand-maintain status.

## Branching and isolation

Use a distinct topic branch and real Git worktree. Stage reviewed paths only;
never stash another session's work or disable verification. Commit, push, open
a PR, merge, publish and deploy each require the applicable user authorization
and checks. Do not automatically merge or remove worktrees after scaffolding.
"""

# ── Package source templates ─────────────────────────────────────────────────

INIT_PY = """\
#!/usr/bin/env python

import importlib
import inspect
import warnings

warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")

__all__: list[str] = []

CORE_MODULES = [
    "{pkg_dir}.api",
    "{pkg_dir}.error_authority",
]

OPTIONAL_MODULES = {{
    "{pkg_dir}.agent_server": "agent",
    "{pkg_dir}.mcp_server": "mcp",{gql_optional_module}
}}


def _import_module_safely(module_name: str):
    \"\"\"Try to import a module and return it, or None if not available.\"\"\"
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def _expose_members(module):
    \"\"\"Expose public classes and functions from a module into globals and __all__.\"\"\"
    for name, obj in inspect.getmembers(module):
        if (inspect.isclass(obj) or inspect.isfunction(obj)) and not name.startswith(
            "_"
        ):
            globals()[name] = obj
            __all__.append(name)


for module_name in CORE_MODULES:
    try:
        module = importlib.import_module(module_name)
        _expose_members(module)
    except ImportError:
        pass

for module_name, extra_name in OPTIONAL_MODULES.items():
    module = _import_module_safely(module_name)
    if module is not None:
        _expose_members(module)
        globals()[f"_{{extra_name.upper()}}_AVAILABLE"] = True
    else:
        globals()[f"_{{extra_name.upper()}}_AVAILABLE"] = False

__all__.extend(["_MCP_AVAILABLE", "_AGENT_AVAILABLE"{gql_all_extend}])
"""


MCP_SERVER_PY = """\
import sys
from pathlib import Path

from agent_connector_sdk.config import load_config
from agent_connector_sdk.mcp.content import ConnectorContent
from agent_connector_sdk.mcp.server import create_mcp_server
from agent_connector_sdk.mcp.tool_surface import register_tool_surface

from . import mcp as tool_modules

__version__ = "0.1.0"


def get_mcp_instance(*, command_args=None):
    \"\"\"Construct one SDK-governed server and its native package content.\"\"\"
    load_config()
    package_root = Path(__file__).resolve().parent
    args, mcp, middlewares = create_mcp_server(
        name="{display_name}",
        version=__version__,
        instructions="{description}",
        command_args=command_args,
        content=ConnectorContent(
            connector="{package_name}",
            package_root=package_root,
            package_version=__version__,
            manifest_path=package_root / "connector_manifest.yml",
        ),
    )
    register_tool_surface(
        mcp, service="{package_name}", tools_module=tool_modules
    )
    for middleware in middlewares:
        mcp.add_middleware(middleware)
    return mcp, args, middlewares


def build_server(*, command_args=None):
    return get_mcp_instance(command_args=command_args)[0]


def mcp_server():
    mcp, args, _ = get_mcp_instance()
    print("Starting {display_name} MCP", file=sys.stderr)
    options = (
        {{}} if args.transport == "stdio" else {{"host": args.host, "port": args.port}}
    )
    mcp.run(transport=args.transport, **options)


if __name__ == "__main__":
    mcp_server()
"""

AGENT_SERVER_PY = """\
#!/usr/bin/python
import logging
import sys
import warnings

from agent_connector_sdk.config import setting

__version__ = "0.1.0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def agent_server():
    from agent_utilities import (
        build_system_prompt_from_workspace,
        create_agent_parser,
        create_agent_server,
        initialize_workspace,
        load_identity,
    )

    warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="fastmcp")

    initialize_workspace()
    meta = load_identity()
    agent_name = setting("DEFAULT_AGENT_NAME", meta.get("name", "{display_name}"))

    print(f"{{agent_name}} v{{__version__}}", file=sys.stderr)
    parser = create_agent_parser()
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    create_agent_server(
        mcp_url=args.mcp_url,
        mcp_config=args.mcp_config or "mcp_config.json",
        host=args.host,
        port=args.port,
        provider=args.provider,
        model_id=args.model_id,
        router_model=args.model_id,
        agent_model=args.model_id,
        base_url=args.base_url,
        api_key=None,
        agent_description=setting(
            "AGENT_DESCRIPTION", meta.get("description", "{description}")
        ),
        system_prompt=setting(
            "AGENT_SYSTEM_PROMPT",
            meta.get("content") or build_system_prompt_from_workspace(),
        ),
        custom_skills_directory=args.custom_skills_directory,
        enable_web_ui=args.web,
        enable_otel=args.otel,
        otel_endpoint=args.otel_endpoint,
        otel_headers=args.otel_headers,
        otel_public_key=args.otel_public_key,
        otel_secret_key=args.otel_secret_key,
        otel_protocol=args.otel_protocol,
        debug=args.debug,
    )


if __name__ == "__main__":
    agent_server()
"""

MAIN_PY = """\
#!/usr/bin/python
from {pkg_dir}.agent_server import agent_server

if __name__ == "__main__":
    agent_server()
"""


API_CLIENT_SYSTEM = """\
from typing import Any

from .api_client_base import ApiClientBase


class ApiClientSystem(ApiClientBase):
    \"\"\"System status and monitoring API operations.\"\"\"

    def get_system_status(self) -> dict[str, Any]:
        \"\"\"Retrieve the status of the target system.\"\"\"
        return self.request("GET", "/health")
"""

API_INIT_PY = """\
from .api_client_base import ApiClientBase
from .api_client_system import ApiClientSystem

__all__ = ["ApiClientBase", "ApiClientSystem"]
"""

ERROR_AUTHORITY_PY = (TEMPLATES_DIR / "error_authority.py").read_text(encoding="utf-8")
ERROR_RENDERING_PY = (TEMPLATES_DIR / "error_rendering.py").read_text(encoding="utf-8")
KISS_CONFIG = (TEMPLATES_DIR / "kiss.toml").read_text(encoding="utf-8")

INPUT_MODELS_PY = """\
#!/usr/bin/python
\"\"\"Pydantic input models for {display_name} API request parameters.\"\"\"

from pydantic import BaseModel, Field


class SystemStatusInput(BaseModel):
    \"\"\"Input model for system status queries.\"\"\"

    verbose: bool | None = Field(
        default=False, description="Return extended status details."
    )
"""

RESPONSE_MODELS_PY = """\
#!/usr/bin/python
\"\"\"Pydantic response models for {display_name} API payloads.\"\"\"

from typing import Any

from pydantic import BaseModel, Field


class SystemStatusResponse(BaseModel):
    \"\"\"Response model for system status queries.\"\"\"

    status: str | None = Field(default=None, description="Service status string.")
    raw: dict[str, Any] | None = Field(
        default=None, description="Raw response payload."
    )
"""

MCP_SYSTEM_PY = """\
import json

from agent_connector_sdk.mcp.action_dispatch import resolve_action
from agent_connector_sdk.mcp.concurrency import run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ..auth import get_client


def register_system_tools(mcp: FastMCP):
    \"\"\"Register system tag dynamic tools.\"\"\"

    @mcp.tool(tags={{"system"}})
    async def system_operations(
        action: str = Field(
            description="Action to perform. Must be one of: 'status', 'info'."
        ),
        params_json: str = Field(
            default="{{}}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        \"\"\"Manage system tag operations. CONCEPT:{concept_prefix}-001\"\"\"
        if ctx:
            await ctx.info("Executing system tool...")

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {{"error": f"Invalid params_json: {{type(e).__name__}}"}}

        kwargs = {{k: v for k, v in kwargs.items() if v is not None}}

        # Action-router trio: resolve_action validates/canonicalizes (and serves the
        # discovery payload), run_blocking runs the sync client call off the event loop.
        resolved = resolve_action(
            action, {{"status", "info"}}, service="{package_name}"
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "status":
            return await run_blocking(client.get_system_status, **kwargs)
        return {{"info": "System operations dynamic placeholder."}}
"""

MCP_INIT_PY = """\
from .mcp_system import register_system_tools

__all__ = ["register_system_tools"]
"""

PKG_MCP_CONFIG_JSON = """\
{
  "mcpServers": {}
}
"""

ROOT_MCP_CONFIG_JSON = """\
{{
  "mcpServers": {{
    "{package_name}": {{
      "command": "uv",
      "args": [
        "run",
        "{mcp_cmd}"
      ],
      "env": {{
        "SYSTEMTOOL": "true",
        "{upper_name}_ALLOW_PLAINTEXT": "false"
      }}
    }}
  }}
}}
"""


def render_main_agent_json(display_name: str, description: str, source: str) -> str:
    """Render the package's canonical main-agent prompt (CONCEPT:AU-ORCH.routing.resolve-body-single-canonical).

    Emits the StructuredPrompt shape — body in ``instructions.core_directive``,
    ``schema_version``/``source`` stamped, composed onto the agent-utilities base
    via ``extends`` — so it passes ``validate_canonical`` / ``check_prompt_schema``.
    """
    import json as _json

    blueprint = {
        "schema_version": "1.0",
        "task": "main-agent",
        "type": "prompt",
        "source": source,
        "description": description,
        "extends": "agent-utilities:base",
        "compose": "append",
        "metadata": {
            "topic": "General Expertise",
            "tone": "technical and precise",
            "style": "professional assistant",
        },
        "identity": {"role": f"{display_name} Agent", "goal": description},
        "instructions": {
            "core_directive": (
                f"# {display_name} Agent\n\n"
                f"You are the {display_name} Agent. {description}\n\n"
                "Use the `mcp-client` universal skill and the reference docs to "
                "discover the exact tags and tools available for your "
                "capabilities.\n\n"
                "### Core Principles\n"
                "* Be concise and efficient.\n"
                "* Use the knowledge graph to discover tools and experts.\n"
                "* Verify your work before concluding."
            )
        },
        "tools": ["workspace-manager", "agent-workflows"],
    }
    return _json.dumps(blueprint, indent=2, ensure_ascii=False) + "\n"


def render_starter_skill(display_name: str, slug: str, description: str) -> str:
    """Render a minimal atomic starter SKILL.md for the package (CONCEPT:OS-5.52).

    Every package ships at least one skill so it contributes to the XDG skills
    library via its ``agent_utilities.skill_providers`` entry-point. Authored to
    the skill-builder atomic standard (kebab name == dir, trigger-oriented
    description, no multi-step DAG) so it passes ``check_atomicity``.
    """
    return f"""---
name: {slug}
description: >-
  {description} Use when working with {display_name} via this package's MCP
  server/agent — discover its tools, run an operation, or check its reference
  docs. Replace this starter skill with real, trigger-oriented capabilities.
license: MIT
tags: [{slug}, starter, mcp]
metadata:
  version: '0.1.0'
---

# {display_name} Starter Skill

Starter skill for the **{display_name}** package. Use the `mcp-client` universal
skill to connect to this package's MCP server and invoke its tools.

## Usage

1. Discover available tools on the package's MCP server.
2. Invoke the relevant tool with the required arguments.
3. Verify the result before concluding.

> Replace this with concrete, trigger-oriented capabilities for {display_name}
> (one capability per skill — keep it atomic).
"""


def render_ontology_init(display_name: str, domain: str) -> str:
    """Data-only ontology subpackage docstring (CONCEPT:AU-KG.ontology.federation-provider-leg)."""
    return (
        f'"""{display_name} ontology contribution '
        "(CONCEPT:AU-KG.ontology.federation-provider-leg).\n\n"
        f"Data-only subpackage carrying ``{domain}.ttl`` (the ``owl:Ontology``\n"
        f"``http://knuckles.team/kg/{domain}`` module) which the agent-utilities hub\n"
        "federates via the ``agent_utilities.ontology_providers`` entry-point.\n"
        '"""\n'
    )


def render_ontology_ttl(display_name: str, domain: str) -> str:
    """Per-package OWL/RDF stub in the shared kg# namespace — hand-expand it."""
    cap = "".join(w.capitalize() for w in domain.replace("-", " ").split())
    t = """@prefix : <http://knuckles.team/kg#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# TODO: replace this stub with the real domain model. Classes/properties live in the
# SHARED : (kg#) namespace; only the owl:Ontology node gets the per-package IRI. Do NOT
# redefine classes another package owns (:MediaAsset/:Blob/:Document/:Person) — reuse them.

:__CAP__Resource a owl:Class ;
    rdfs:label "__DISPLAY__ Resource" ;
    rdfs:comment "A primary object managed by __DISPLAY__ (STUB — rename/expand)." .

:managedBy a owl:ObjectProperty ;
    rdfs:label "managed by" ;
    rdfs:comment "Links a __DISPLAY__ resource to the Person responsible (STUB)." ;
    rdfs:domain :__CAP__Resource ;
    rdfs:range :Person .

:__DOMAIN__Id a owl:DatatypeProperty ;
    rdfs:label "__DOMAIN__ id" ;
    rdfs:comment "External identifier of the __DISPLAY__ resource (STUB)." ;
    rdfs:domain :__CAP__Resource ;
    rdfs:range xsd:string .

<http://knuckles.team/kg/__DOMAIN__> a owl:Ontology ;
    rdfs:label "__DISPLAY__ Ontology" ;
    rdfs:comment "__DISPLAY__ domain extensions federated into the KG hub. STUB." ;
    owl:imports <http://knuckles.team/kg> .
"""
    return (
        t.replace("__CAP__", cap)
        .replace("__DISPLAY__", display_name)
        .replace("__DOMAIN__", domain.replace("-", ""))
    )


def render_specialist_prompt(display_name: str, source: str, domain: str) -> str:
    """A domain-specialist StructuredPrompt template (beyond the generic main-agent)."""
    import json as _json

    blueprint = {
        "task": f"{domain.replace('-', '_')}_specialist",
        "type": "prompt",
        "schema_version": "1.0",
        "prompt_version": "0.1.0",
        "source": source,
        "extends": "agent-utilities:base",
        "compose": "append",
        "description": f"{display_name} domain specialist. TODO: scope to a tool-category.",
        "metadata": {
            "topic": display_name,
            "tone": "technical and precise",
            "style": f"{display_name} specialist",
        },
        "identity": {
            "role": f"{display_name} Specialist",
            "goal": f"Operate {display_name} and map its data into the knowledge graph.",
            "personality": ["methodical", "provenance-aware"],
        },
        "instructions": {
            "core_directive": (
                f"You are a {display_name} specialist. Prefer the domain-typed tools/skills; "
                "ingest only records authorized for the configured source binding. "
                "TODO: tailor to a specific tool-category."
            ),
            "quality_checklist": [
                "used the domain-typed tool",
                "preserved the caller authorization and source provenance",
            ],
        },
        "skills": [],
        "tools": [],
    }
    return _json.dumps(blueprint, indent=2, ensure_ascii=False) + "\n"


def render_source_presets(package_name: str, domain: str) -> str:
    """In-repo Tier-1 mcp_tool source-preset stub (hub-side pull; complements native push)."""
    import json as _json

    data = {
        "_comment": (
            "Tier-1 mcp_tool source preset(s) (AU-KG.ingest.mcp-tool-connector). Hand-fill: "
            "tool, action, records_path, id/title/text/updated fields, pagination. "
            "Contributed presets win over the central MCP_TOOL_PRESETS."
        ),
        f"{domain}-records": {
            "server": package_name,
            "tool": f"TODO_{domain.replace('-', '_')}_list_tool",
            "action": "list",
            "records_path": "data",
            "id_field": "id",
            "title_field": "name",
            "text_field": "description",
            "updated_field": "updated_at",
            "doc_type": domain,
        },
    }
    return _json.dumps(data, indent=2, ensure_ascii=False) + "\n"


GQL_PY = r'''"""GraphQL operations over the same governed SDK transport as REST."""
from typing import Any
from .api.api_client_base import ApiClientBase


class GraphQL(ApiClientBase):
    def execute_gql(self, query_str: str, variables: dict[str, Any] | None = None,
                    operation_name: str | None = None) -> dict[str, Any]:
        if not isinstance(query_str, str) or not query_str.strip() or len(query_str) > 1_000_000:
            raise ValueError("GraphQL query exceeds its input boundary")
        result = self.request("POST", "/api/graphql", json={{
            "query": query_str, "variables": variables or {{}}, "operationName": operation_name,
        }})
        if "errors" in result:
            raise RuntimeError("GraphQL operation failed; partial results were not accepted")
        return result
'''

VALIDATE_AGENT_PY = """\
#!/usr/bin/env python3
\"\"\"Smoke-validate the A2A agent server entry point.\"\"\"

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from {pkg_dir}.agent_server import agent_server  # noqa: F401
except ImportError as e:
    print(f"Agent import failed: {{type(e).__name__}}")
    sys.exit(1)

print("Agent entry point import OK")
"""

# ── mkdocs + docs site (7 standard pages) ─────────────────────────────────────

MKDOCS_YML = """\
INHERIT: .pipeline-theme/templates/mkdocs-theme/base.mkdocs.yml
site_name: "{package_name}"
site_description: "{description}"
site_url: "https://knuckles-team.github.io/{package_name}/"
repo_name: "Knuckles-Team/{package_name}"
repo_url: "https://github.com/Knuckles-Team/{package_name}"
edit_uri: "edit/main/docs/"
copyright: "Copyright &copy; Knuckles-Team — MIT licensed"

plugins:
  - search

extra:
  ecosystem:
    current: "{package_name}"

nav:
  - Home: index.md
  - Overview: overview.md
  - Architecture: architecture.md
  - Installation: installation.md
  - Deployment: deployment.md
  - Usage (API / CLI / MCP): usage.md
  - Backing Platform ({display_name}): platform.md
  - Concepts: concepts.md
  - Glossary: glossary.md
  - Spec delivery: spec-delivery.md
"""

DOCS_INDEX_MD = """\
# {package_name}

{display_name} **API + MCP Server + A2A Agent** for the agent-utilities ecosystem — a
typed, action-routed connector.

!!! info "Official documentation"
    This site is the canonical reference for `{package_name}`, maintained alongside
    every release.

[![PyPI](https://img.shields.io/pypi/v/{package_name})](https://pypi.org/project/{package_name}/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/{package_name})](https://github.com/Knuckles-Team/{package_name}/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/{package_name})

## Overview

`{package_name}` wraps the target service with typed, deterministic MCP tools and an
optional Pydantic-AI agent server.

Tools resolve `{upper_name}_BASE_URL`, `{upper_name}_TOKEN_REF`, and the SDK TLS
profile when invoked. Discovery requires no vendor credentials or live service.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Installation](installation.md)** — pip, source, extras, and the prebuilt Docker image.
- :material-server-network: **[Deployment](deployment.md)** — run local transports or connect through an authenticated TLS ingress.
- :material-console: **[Usage](usage.md)** — the MCP tools, the Python client, and the CLI.
- :material-database-cog: **[Backing Platform](platform.md)** — deploy the target service with Docker.
- :material-sitemap: **[Overview](overview.md)** — the action-routed tool surface and architecture.
- :material-graph: **[Concepts](concepts.md)** — the CONCEPT ID registry.

</div>
"""

DOCS_OVERVIEW_MD = """\
# {package_name} — Concept Overview

> **Category**: Integration | **Ecosystem Role**: MCP Server + A2A Agent
> Built on [`agent-utilities`](https://github.com/Knuckles-Team/agent-utilities) — the unified AGI Harness.

## Description

{description}

## Architecture

This project follows the standardized agent-package pattern:

- **Modular Design**: split into `api/` (client mixins) and `mcp/` (action-routed
  tool modules) for cleaner organization.
- **Dynamic Tool Registration**: action-routed dynamic tool tags, strictly
  lowercase, each togglable with a `*TOOL` environment flag.
- **A2A Agent Server**: a Pydantic-AI graph agent (console script `{agent_cmd}`)
  that calls the MCP tool surface and exposes an AG-UI web interface.

## Concept Registry

This project implements or inherits the following ecosystem concepts:

| Concept ID | Description | Source |
|:-----------|:------------|:-------|
| ECO-4.1 | MCP & Universal Skills | `agent-utilities` (inherited) |
| ECO-4.2 | A2A Network & Consensus | `agent-utilities` (inherited) |

> 📖 **Full Registry**: See [`agent-utilities/docs/overview.md`](https://github.com/Knuckles-Team/agent-utilities/blob/main/docs/overview.md) for the complete 5-Pillar concept index.
"""

DOCS_INSTALLATION_MD = """\
# Installation

`{package_name}` is a standard Python package and a prebuilt container image.

## Requirements

- **Python 3.12–3.14**.
- SDK configuration containing the service origin, a credential reference and TLS profile selectors.

## From PyPI (recommended)

```bash
pip install {package_name}
```

### Optional extras

| Extra | Install | Pulls in |
|---|---|---|
| `mcp` | `pip install "{package_name}[mcp]"` | MCP runtime + SDK graph client |
| `agent` | `pip install "{package_name}[agent]"` | Current agent runtime + Logfire tracing |
| `all` | `pip install "{package_name}[all]"` | Everything above |

## From source

```bash
git clone https://github.com/Knuckles-Team/{package_name}.git
cd {package_name}
pip install -e ".[all]"
```

## Docker

```bash
IMAGE_REF='<registry>/{package_name}@sha256:<digest>'
docker pull "$IMAGE_REF"
```
"""

DOCS_DEPLOYMENT_MD = """\
# Deployment

This page covers running `{package_name}` as long-lived servers.

## Build from a reviewed source commit

The production Dockerfile installs the local package and its selected runtime
extra from the repository root. It does not download `{package_name}` from an
index. The build copies the complete `{pkg_dir}/` directory, including generated
OpenAPI contracts, prompts, skills, ontology and connector data. Runtime images
contain the installed package; source tooling remains outside the final stage.

Use an exact reviewed commit as the build context:

```bash
SOURCE_COMMIT=$(git rev-parse --verify 'HEAD^{{commit}}')
git archive --format=tar "$SOURCE_COMMIT" | docker build \\
  --file docker/Dockerfile --target mcp \\
  --label "org.opencontainers.image.revision=$SOURCE_COMMIT" \\
  --tag {package_name}:mcp-local -
```

For an enabled agent surface, select `--target agent`. The shared
[container workflow](https://github.com/Knuckles-Team/pipelines/blob/7b3d18d72b5622d455ece3bbe45a9482bc6e8b5e/.github/workflows/container_pipeline.yml)
also checks out the exact workflow commit. Build only on an approved image-build
host. Publish through the repository's approved process, then deploy the returned
image manifest digest through `MCP_IMAGE` (and `AGENT_IMAGE` when enabled).
A source commit does not freeze the index-resolved dependency closure. For a
qualified offline wheel build, use the shared
[runtime artifact contract](https://github.com/Knuckles-Team/pipelines/blob/7b3d18d72b5622d455ece3bbe45a9482bc6e8b5e/reference/container-runtime.md)
with its producer receipts and full hashes. This scaffold does not claim that
qualification or provision a producer, registry credentials or deployment.

> `{package_name}` ships both an **MCP server** (console script `{mcp_cmd}`) and an
> **A2A agent server** (console script `{agent_cmd}`).

<!-- BEGIN GENERATED: deployment-options -->
## Deployment Options

`{package_name}` exposes its MCP server (console script `{mcp_cmd}`) four ways. Pick the
row that matches where the server runs relative to your MCP client, then copy the
matching `mcp_config.json` below.

| # | Option | Transport | Where it runs | `mcp_config.json` key |
|---|--------|-----------|---------------|------------------------|
| 1 | stdio | `stdio` | client launches a subprocess | `command` |
| 2 | Streamable-HTTP (local) | `streamable-http` | a local network port | `command` or `url` |
| 3 | Local container | `stdio` | reviewed Docker / Podman image on this host | `command` |
| 4 | Remote URL | `streamable-http` | operator-owned authenticated TLS ingress | `url` |

### 1. stdio (local subprocess)

```json
{{
  "mcpServers": {{
    "{mcp_cmd}": {{
      "command": "{mcp_cmd}",
      "args": [],
      "env": {{
        "SYSTEMTOOL": "true"
      }}
    }}
  }}
}}
```

### 2. Streamable-HTTP (local process)

```bash
{mcp_cmd} --transport streamable-http --host 127.0.0.1 --port 8000
curl -s http://loopback.invalid:8000/health        # {{"status":"OK"}}
```

Connect to the running process by URL:

```json
{{
  "mcpServers": {{
    "{mcp_cmd}": {{ "url": "http://loopback.invalid:8000/mcp" }}
  }}
}}
```

### 3. Local container

Launch a container directly from `mcp_config.json` (swap `docker` for `podman` for a
daemonless runtime):

```json
{{
  "mcpServers": {{
    "{mcp_cmd}": {{
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "--read-only", "--cap-drop=ALL",
        "--security-opt=no-new-privileges", "--pids-limit=256",
        "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=64m",
        "-e", "TRANSPORT=stdio",
        "<registry>/{package_name}@sha256:<digest>"
      ]
    }}
  }}
}}
```

Supply the provider profile through the operator-owned connector configuration mount or secret
projection. The image and this document contain no endpoint, credential, or trust material.

### 4. Remote URL (authenticated TLS ingress)

When the server is deployed remotely, connect through its operator-supplied
authenticated HTTPS ingress; no local process or image is required:

```json
{{
  "mcpServers": {{
    "{mcp_cmd}": {{ "url": "https://service.example.invalid/mcp" }}
  }}
}}
```

Configure outbound MCP identity and trust references in SDK configuration. The server
must use direct TLS or an explicitly trusted TLS-terminating ingress and an exact
`MCP_ALLOWED_HOSTS` policy; do not commit the endpoint, credentials, or trust paths.
<!-- END GENERATED: deployment-options -->

## Docker Compose

```bash
docker compose -f docker/mcp.compose.yml up -d      # MCP server only
docker compose -f docker/agent.compose.yml up -d    # MCP + agent
```

## Run the A2A agent server

```bash
{agent_cmd} --mcp-config mcp_config.json --web
```
"""

DOCS_USAGE_MD = """\
# Usage — API / CLI / MCP

`{package_name}` exposes the same capability three ways: as **MCP tools** an agent
calls, as a **Python API** you import, and as a **CLI**.

## As an MCP server

Once [deployed](deployment.md), the server registers consolidated, action-routed
tool modules. Each module is independently togglable with a `*TOOL` environment
flag.

## As a Python API

```python
from {pkg_dir}.auth import get_client

api = get_client()        # resolves SDK settings and credential references
status = api.get_system_status()
```

## As a CLI

Configure `{upper_name}_BASE_URL`, `{upper_name}_TOKEN_REF`, and one SDK TLS profile
selector through operator-provided settings, then run `{mcp_cmd} --transport stdio`.

### Explicit HTTP endpoint

HTTPS remains the default. For an existing HTTP-only endpoint you are authorized
to use, set `{upper_name}_BASE_URL=http://service.example.invalid` and explicitly
set `{upper_name}_ALLOW_PLAINTEXT=true`. This forwards the SDK's
`HttpClientOptions.allow_plaintext` choice only to that vendor client. Requests
remain bound to its exact scheme, host and port; redirects stay disabled.
HTTP carries requests without TLS encryption. The flag never retries HTTPS over
HTTP, changes certificate verification, or authorizes another endpoint. OIDC
token exchanges retain their separate TLS policy. Leave the flag false for HTTPS.
"""

DOCS_PLATFORM_MD = """\
# Backing Platform — {display_name}

`{package_name}` is a **client** of a backing service instance. This page provides a
Docker recipe for deploying one locally as an operator-selected provider endpoint.

!!! note "Backing-system recipe"
    Each connector in the ecosystem follows the same convention — a
    `docs/platform.md` recipe for the system it integrates with, accompanied by a
    sample Compose stack. Systems offered only as a managed service have no local
    recipe.

## Single-node deployment (Compose)

```yaml
# docker/platform.compose.yml — replace with the real backing-service recipe
services:
  platform:
    image: REPLACE_ME
    restart: unless-stopped
    ports:
      - "8080:8080"
```
"""

DOCS_CONCEPTS_MD = """\
# Concept Registry — {package_name}

> **Prefix**: `CONCEPT:{concept_prefix}-*`
> **Version**: 0.1.0
> **Bridge**: [`CONCEPT:ECO-4.0`](https://github.com/Knuckles-Team/agent-utilities/blob/main/docs/concepts.md) (Unified Toolkit Ingestion)

---

## Project-Specific Concepts

| Concept ID | Name | Description |
|------------|------|-------------|
| `CONCEPT:{concept_prefix}-001` | System Operations | MCP tool domain `system` — Action-routed dynamic tool registration |

## Cross-Project References (from agent-utilities)

| Concept ID | Name | Origin |
|------------|------|--------|
| `CONCEPT:ECO-4.0` | Unified Toolkit Ingestion | agent-utilities |
| `CONCEPT:ORCH-1.2` | Confidence-Gated Router | agent-utilities |
| `CONCEPT:OS-5.1` | Prompt Injection Defense | agent-utilities |
"""

AGENT_READINESS_JSON = """\
{{
  "schema_version": "agent-readiness/v1",
  "project": {{"name": "{package_name}", "kind": "package"}},
  "applicability": {{
    "content": true,
    "discoverability": true,
    "access_policy": true,
    "capabilities": true,
    "errors": true,
    "provenance": true,
    "measurement": false,
    "deployment": false
  }},
  "standards": [
    {{"id": "RFC 3986", "kind": "rfc", "level": "normative"}},
    {{"id": "RFC 9264", "kind": "rfc", "level": "normative"}},
    {{"id": "RFC 9727", "kind": "rfc", "level": "normative"}},
    {{"id": "RFC 8414", "kind": "rfc", "level": "normative"}},
    {{"id": "RFC 9728", "kind": "rfc", "level": "normative"}},
    {{"id": "Agent Documentation Standard vNext", "kind": "draft", "level": "draft"}},
    {{"id": "Concept IDs and AGENTS", "kind": "convention", "level": "advisory"}}
  ],
  "content_signals": {{"policy": "unset"}},
  "budgets": {{"curated_chars": 24000, "summary_chars": 800, "full_chars": 0}},
  "capabilities": {{
    "api": {{"applicable": {api_applicable}{api_artifact}}},
    "mcp": {{"applicable": {mcp_applicable}{mcp_artifact}}},
    "a2a": {{"applicable": {a2a_applicable}{a2a_artifact}}},
    "skills": {{"applicable": true, "path": "{pkg_dir}/skills"}}
  }}
}}
"""

CAPABILITY_API_JSON = """\
{{"applicable": true, "surface": "api", "version": "capability/v1", "source": "{pkg_dir}/api/__init__.py"}}
"""
CAPABILITY_MCP_JSON = """\
{{"applicable": true, "surface": "mcp", "version": "capability/v1", "http_transport": true, "source": "{pkg_dir}/mcp_server.py"}}
"""
CAPABILITY_A2A_JSON = """\
{{"applicable": true, "surface": "a2a", "version": "capability/v1", "source": "{pkg_dir}/agent_server.py"}}
"""

# ── Tests ─────────────────────────────────────────────────────────────────────

TESTS_CONFTEST = """\
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_api_client():
    client = MagicMock()
    client.get_system_status.return_value = {{"status": "OK"}}
    return client
"""


TESTS_ERROR_AUTHORITY = """\
import json

import pytest

from {pkg_dir}.error_authority import (
    BROWSER_HTML_MEDIA_TYPE,
    MAX_DETAIL_CHARS,
    PROBLEM_JSON_MEDIA_TYPE,
    STRUCTURED_MARKDOWN_MEDIA_TYPE,
    ProblemDetails,
    render_error,
)


@pytest.mark.concept("{concept_prefix}-001")
def test_agent_representations_share_metadata():
    problem = ProblemDetails(
        status=503,
        code="dependency_unavailable",
        type_uri="urn:agent-error:dependency-unavailable",
        instance="urn:request:abc123",
        detail="The upstream is temporarily unavailable.",
        retryable=True,
        retry_after_s=12,
    )
    json_response = render_error(problem, accept=PROBLEM_JSON_MEDIA_TYPE)
    markdown_response = render_error(problem, accept=STRUCTURED_MARKDOWN_MEDIA_TYPE)
    payload = json.loads(json_response.body)

    assert json_response.media_type == PROBLEM_JSON_MEDIA_TYPE
    assert markdown_response.media_type == STRUCTURED_MARKDOWN_MEDIA_TYPE
    assert json_response.headers["Vary"] == "Accept"
    assert json_response.headers["Retry-After"] == "12.0"
    for field, value in problem.metadata().items():
        assert payload[field] == value
        assert field + ": " + json.dumps(value) in markdown_response.body


def test_denial_is_never_retryable_and_detail_is_bounded():
    denied = ProblemDetails(
        status=403,
        code="permission_denied",
        instance="urn:request:denied",
        detail=("/home/operator/private-token " + ("x" * (MAX_DETAIL_CHARS + 100))),
        retryable=True,
        retry_after_s=30,
    )
    response = render_error(denied, accept=PROBLEM_JSON_MEDIA_TYPE)
    payload = json.loads(response.body)

    assert payload["retryable"] is False
    assert payload["retry_after_s"] is None
    assert len(payload["detail"]) <= MAX_DETAIL_CHARS
    assert "/home/operator" not in payload["detail"]


def test_browser_html_is_retained_for_browser_accept_headers():
    problem = ProblemDetails(
        status=400,
        code="invalid_request",
        instance="urn:request:browser",
        detail="The request is invalid.",
    )
    response = render_error(problem, accept="text/html,application/xhtml+xml")

    assert response.media_type == BROWSER_HTML_MEDIA_TYPE
    assert response.body.startswith("<!doctype html>")
    assert 'data-error-code="invalid_request"' in response.body
"""

TESTS_MCP_VALIDATION = """\
import pytest

from {pkg_dir}.mcp_server import get_mcp_instance


@pytest.mark.concept("{concept_prefix}-001")
def test_mcp_instance_registration(monkeypatch):
    \"\"\"MCP server instantiates with its tool domains registered.

    CONCEPT:{concept_prefix}-001
    \"\"\"
    monkeypatch.setattr("sys.argv", ["{mcp_cmd}"])
    mcp, args, middlewares = get_mcp_instance()
    assert mcp is not None
"""

TESTS_INIT_DYNAMICS = """\
import importlib

import pytest


@pytest.mark.concept("{concept_prefix}-001")
def test_package_imports():
    \"\"\"Top-level package exposes its public API. CONCEPT:{concept_prefix}-001\"\"\"
    module = importlib.import_module("{pkg_dir}")
    assert hasattr(module, "__all__")
"""

TESTS_STARTUP = """\
import importlib

import pytest


@pytest.mark.concept("{concept_prefix}-001")
def test_mcp_server_module_importable():
    \"\"\"MCP server module imports cleanly at startup. CONCEPT:{concept_prefix}-001\"\"\"
    assert importlib.import_module("{pkg_dir}.mcp_server") is not None
"""

TESTS_CONCEPT_PARITY = """\
from pathlib import Path

import pytest

CONCEPTS_DOC = Path(__file__).resolve().parents[1] / "docs" / "concepts.md"


@pytest.mark.concept("{concept_prefix}-001")
def test_concepts_doc_exists():
    \"\"\"Concept registry doc exists. CONCEPT:{concept_prefix}-001\"\"\"
    assert CONCEPTS_DOC.is_file()


@pytest.mark.concept("{concept_prefix}-001")
def test_eco_bridge_present():
    \"\"\"ECO-4.0 bridge concept is referenced. CONCEPT:{concept_prefix}-001\"\"\"
    assert "ECO-4.0" in CONCEPTS_DOC.read_text(encoding="utf-8")


@pytest.mark.concept("{concept_prefix}-001")
def test_prefix_registered():
    \"\"\"Project concept prefix is registered. CONCEPT:{concept_prefix}-001\"\"\"
    assert "CONCEPT:{concept_prefix}-" in CONCEPTS_DOC.read_text(
        encoding="utf-8"
    )
"""


# ── Main Scaffolding Logic ───────────────────────────────────────────────────


def scaffold(
    package_name: str,
    output_dir: str = ".",
    pkg_types: str = "api_client,mcp",
    display_name: str = "",
    description: str = "",
    concept_prefix: str = "",
    doc_urls: str = "",
    in_place: bool = False,
    generated_on: str | None = None,
):
    """Scaffold a complete agent-package project (SDK contracts)."""
    types = set(pkg_types.split(","))
    types = {value.strip() for value in types}
    supported = {"api_client", "cli", "mcp", "agent", "graphql"}
    backends = types & {"api_client", "cli"}
    if (
        len(backends) != 1
        or "mcp" not in types
        or not types <= supported
        or ("graphql" in types and "api_client" not in types)
    ):
        raise ValueError(
            "--type requires api_client,mcp or cli,mcp; optional addition: agent; "
            "graphql is supported only with api_client"
        )
    backend = next(iter(backends))
    has_agent = "agent" in types
    pkg_dir = to_pkg_dir(package_name)
    if not display_name:
        display_name = to_display(package_name)
    if not description:
        label = "API" if backend == "api_client" else "CLI"
        description = f"{display_name} {label} + MCP Server" + (
            " + A2A Server" if has_agent else ""
        )
    upper_name = to_upper_env(package_name)
    if not concept_prefix:
        concept_prefix = upper_name.split("_")[0]

    # Derived names: console scripts strip a trailing -mcp/-agent/-api suffix.
    parts = package_name.rsplit("-", 1)
    if len(parts) == 2 and parts[1] in ("mcp", "agent", "api"):
        mcp_cmd = f"{parts[0]}-mcp"
        agent_cmd = f"{parts[0]}-agent"
        short_name = parts[0]
    else:
        mcp_cmd = f"{package_name}-mcp"
        agent_cmd = f"{package_name}-agent"
        short_name = package_name

    generated = generation_date(generated_on)
    year = generated.year
    date = generated.isoformat()

    has_graphql = "graphql" in types
    gql_core_dep = ' "gql[requests]>=4.0.0",' if has_graphql else ""
    gql_extra = 'gql = [ "gql[requests]>=4.0.0",]\n' if has_graphql else ""
    gql_all_dep = ' "gql[requests]>=4.0.0",' if has_graphql else ""
    gql_module_name = f"{to_pkg_dir(short_name)}_gql"
    gql_optional_module = (
        f'\n    "{pkg_dir}.{gql_module_name}": "gql",' if has_graphql else ""
    )
    gql_all_extend = ', "_GQL_AVAILABLE"' if has_graphql else ""

    ctx = {
        "package_name": package_name,
        "pkg_dir": pkg_dir,
        "display_name": display_name,
        "description": description,
        "backend": backend,
        "has_agent": has_agent,
        "badge_lines": render_public_badges(package_name, mcp_server="mcp" in types),
        "mcp_server": "true" if "mcp" in types else "false",
        "concept_prefix": concept_prefix,
        "mcp_cmd": mcp_cmd,
        "agent_cmd": agent_cmd,
        "agent_entry": f'{agent_cmd} = "{pkg_dir}.agent_server:agent_server"'
        if "agent" in types
        else "",
        "short_name": short_name,
        "agent_port": "9000",
        "gql_core_dep": gql_core_dep,
        "gql_extra": gql_extra,
        "gql_all_dep": gql_all_dep,
        "gql_optional_module": gql_optional_module,
        "gql_all_extend": gql_all_extend,
        "api_applicable": "true" if "api_client" in types else "false",
        "mcp_applicable": "true" if "mcp" in types else "false",
        "a2a_applicable": "true" if "agent" in types else "false",
        "api_artifact": (
            ', "artifact": "docs/capabilities/api.json"'
            if "api_client" in types
            else ""
        ),
        "mcp_artifact": (
            ', "artifact": "docs/capabilities/mcp.json"' if "mcp" in types else ""
        ),
        "a2a_artifact": (
            ', "artifact": "docs/capabilities/a2a.json"' if "agent" in types else ""
        ),
        "year": year,
        "date": date,
        "upper_name": upper_name,
    }

    root = (Path(output_dir) if in_place else Path(output_dir) / package_name).resolve()
    validate_theme_destinations(root, (Path(".pipeline-theme"),))
    pkg = root / pkg_dir

    # files: path -> (template, needs_format)
    files = {
        # Root configs
        root / "pyproject.toml": (PYPROJECT_TOML, True),
        root / ".bumpversion.cfg": (BUMPVERSION_CFG, True),
        root / ".pre-commit-config.yaml": (
            PRECOMMIT_CONFIG.replace("__PACKAGE__", pkg_dir),
            False,
        ),
        root / ".dockerignore": (DOCKERIGNORE, True),
        root / ".env.example": (ENV_EXAMPLE, True),
        root / ".gitignore": (GITIGNORE, False),
        root / ".gitattributes": (GITATTRIBUTES, False),
        root / ".codespellignore": (CODESPELLIGNORE, False),
        root / ".vulture_ignore": (VULTURE_IGNORE, False),
        root / "pytest.ini": (PYTEST_INI, False),
        root / "a2a.json": (A2A_JSON, True),
        root / "opencode.json": (OPENCODE_JSON, False),
        root / "mcp_config.json": (ROOT_MCP_CONFIG_JSON, True),
        root / "AGENTS.md": (ROOT_AGENTS_MD, True),
        root / "CLAUDE.md": (CLAUDE_MD, False),
        root / "LICENSE": (LICENSE_MIT, True),
        root / "MANIFEST.in": (MANIFEST_IN, True),
        root / "README.md": (README_MD, True),
        root / "CHANGELOG.md": (CHANGELOG_MD, True),
        # Docker
        root / "docker/Dockerfile": (DOCKERFILE, True),
        root / "docker/debug.Dockerfile": (DEBUG_DOCKERFILE, True),
        root / "docker/agent.compose.yml": (AGENT_COMPOSE_YML, True),
        root / "docker/mcp.compose.yml": (MCP_COMPOSE_YML, True),
        root / "docker/starship.toml": (STARSHIP_TOML, True),
        # GitHub workflows
        root / ".github/workflows/pipeline.yml": (PIPELINE_YML, False),
        root / ".github/workflows/scanners.yml": (SCANNER_CI_YML, False),
        root / ".github/workflows/pages.yml": (PAGES_YML, False),
        root / ".github/workflows/windows-ci.yml": (WINDOWS_CI_YML, True),
        # Docs site (7 standard pages)
        root / "mkdocs.yml": (MKDOCS_YML, True),
        root / ".config/spec-dashboard.json": (SPEC_DASHBOARD_CONFIG, False),
        root / ".config/kiss.toml": (KISS_CONFIG, False),
        root / "docs/spec-delivery.md": (SPEC_DELIVERY_MD, True),
        root / "docs/index.md": (DOCS_INDEX_MD, True),
        root / "docs/overview.md": (DOCS_OVERVIEW_MD, True),
        root / "docs/installation.md": (DOCS_INSTALLATION_MD, True),
        root / "docs/deployment.md": (DOCS_DEPLOYMENT_MD, True),
        root / "docs/usage.md": (DOCS_USAGE_MD, True),
        root / "docs/platform.md": (DOCS_PLATFORM_MD, True),
        root / "docs/concepts.md": (DOCS_CONCEPTS_MD, True),
        root / "docs/agent-readiness.json": (AGENT_READINESS_JSON, True),
        # Repo scripts
        root / "scripts/validate_agent.py": (VALIDATE_AGENT_PY, True),
    }

    if "api_client" in types:
        files[root / "docs/capabilities/api.json"] = (CAPABILITY_API_JSON, True)

    # Package files
    files[pkg / "__init__.py"] = (INIT_PY, True)
    files[pkg / "error_authority.py"] = (ERROR_AUTHORITY_PY, False)
    files[pkg / "error_rendering.py"] = (ERROR_RENDERING_PY, False)
    if backend == "api_client":
        files[pkg / "auth.py"] = (AUTH_PY, True)
        files[pkg / f"{to_pkg_dir(short_name)}_input_models.py"] = (
            INPUT_MODELS_PY,
            True,
        )
        files[pkg / f"{to_pkg_dir(short_name)}_response_models.py"] = (
            RESPONSE_MODELS_PY,
            True,
        )
    else:
        files[pkg / "cli.py"] = (CLI_PY, True)
    files[pkg / "mcp_config.json"] = (PKG_MCP_CONFIG_JSON, False)

    # Canonical system prompt (CONCEPT:AU-ORCH.routing.resolve-body-single-canonical) + fleet contribution
    # (CONCEPT:OS-5.52). The prompt lives in a `prompts/` data subpackage (the
    # agent_utilities.prompt_providers entry-point target) and is mirrored at the
    # package root where the runtime workspace loader reads it. Both render from
    # ONE helper so they cannot drift.
    main_agent_content = render_main_agent_json(display_name, description, package_name)
    files[pkg / "main_agent.json"] = (main_agent_content, False)
    files[pkg / "prompts" / "__init__.py"] = ("", False)
    files[pkg / "prompts" / "main_agent.json"] = (main_agent_content, False)

    # Starter skill (CONCEPT:OS-5.52): every package ships >=1 skill so it
    # contributes to the XDG skills library via its skill_providers entry-point.
    # NOTE: replace this starter with REAL per-tool-category skills (`{short}-<category>`,
    # globally unique) before shipping — see PARITY_MANIFEST §6.
    starter_slug = f"{short_name}-starter"
    files[pkg / "skills" / "__init__.py"] = ("", False)
    files[pkg / "skills" / starter_slug / "SKILL.md"] = (
        render_starter_skill(display_name, starter_slug, description),
        False,
    )

    # KG enrichment legs (CONCEPT:AU-KG.ontology.federation-provider-leg /
    # AU-KG.ingest.enterprise-source-extractor): the ontology, native "maximum ingestion"
    # (typed nodes + documents + blobs) via the shared native_ingest primitive, a
    # domain-specialist prompt, and an in-repo source-connector preset. Hand-expand the
    # STUBS — see PARITY_MANIFEST §6 and the gitlab-api / media-downloader reference impls.
    ontology_domain = short_name
    files[pkg / "ontology" / "__init__.py"] = (
        render_ontology_init(display_name, ontology_domain),
        False,
    )
    files[pkg / "ontology" / f"{ontology_domain}.ttl"] = (
        render_ontology_ttl(display_name, ontology_domain),
        False,
    )
    files[pkg / "kg_ingest.py"] = (
        render_kg_ingest(display_name, pkg.name, package_name, ontology_domain),
        False,
    )
    files[pkg / "prompts" / f"{ontology_domain.replace('-', '_')}_specialist.json"] = (
        render_specialist_prompt(display_name, package_name, ontology_domain),
        False,
    )
    files[pkg / "connectors" / "__init__.py"] = ("", False)
    files[pkg / "connectors" / "mcp_source_presets.json"] = (
        "{}\n",
        False,
    )
    files[root / "tests" / "test_kg_ingest.py"] = (
        render_kg_ingest_test(pkg.name),
        False,
    )

    files[pkg / "connector_manifest.yml"] = (
        render_connector_manifest(
            package_name,
            ontology_domain,
            render_ontology_ttl(display_name, ontology_domain),
        ),
        False,
    )
    files[pkg / "connectors" / "tool_schema_fingerprints.json"] = (
        render_empty_fingerprints(package_name),
        False,
    )
    files[root / "scripts" / "generate_tool_schemas.py"] = (
        render_schema_generator(pkg_dir, package_name),
        False,
    )

    # Backend source is emitted only for the selected integration boundary.
    if backend == "api_client":
        files[pkg / "api" / "__init__.py"] = (API_INIT_PY, False)
        files[pkg / "api" / "api_client_base.py"] = (API_CLIENT_BASE, True)
        files[pkg / "api" / "api_client_system.py"] = (API_CLIENT_SYSTEM, True)

    # MCP modular directory scaffolding
    files[pkg / "mcp" / "__init__.py"] = (MCP_INIT_PY, False)
    files[pkg / "mcp" / "mcp_system.py"] = (
        CLI_MCP_SYSTEM_PY if backend == "cli" else MCP_SYSTEM_PY,
        True,
    )

    if "mcp" in types:
        files[pkg / "mcp_server.py"] = (MCP_SERVER_PY, True)
        files[root / "docs/capabilities/mcp.json"] = (CAPABILITY_MCP_JSON, True)

    if "agent" in types:
        files[pkg / "agent_server.py"] = (AGENT_SERVER_PY, True)
        files[pkg / "__main__.py"] = (MAIN_PY, True)
        files[root / "docs/capabilities/a2a.json"] = (CAPABILITY_A2A_JSON, True)

    if has_graphql:
        files[pkg / f"{gql_module_name}.py"] = (GQL_PY, True)

    if "agent" not in types:
        for optional_path in (
            root / "a2a.json",
            root / "scripts/validate_agent.py",
            root / "docker/agent.compose.yml",
        ):
            files.pop(optional_path, None)
        files[pkg / "__main__.py"] = (
            "from .mcp_server import mcp_server\n\nif __name__ == '__main__':\n    mcp_server()\n",
            False,
        )

    # Flat tests directory
    files[root / "tests" / "__init__.py"] = ("", False)
    if backend == "api_client":
        files[root / "tests" / "conftest.py"] = (TESTS_CONFTEST, True)
        files[root / "tests" / "test_auth.py"] = (TESTS_AUTH, True)
        files[root / "tests" / "test_api_wrapper.py"] = (TESTS_API_WRAPPER, True)
    else:
        files[root / "tests" / "conftest.py"] = ("", False)
        files[root / "tests" / "test_cli.py"] = (TESTS_CLI, True)
    files[root / "tests" / "test_error_authority.py"] = (
        TESTS_ERROR_AUTHORITY,
        True,
    )
    files[root / "tests" / f"test_{to_pkg_dir(short_name)}_mcp_validation.py"] = (
        TESTS_MCP_VALIDATION,
        True,
    )
    files[root / "tests" / "test_init_dynamics.py"] = (TESTS_INIT_DYNAMICS, True)
    files[root / "tests" / "test_startup.py"] = (TESTS_STARTUP, True)
    files[root / "tests" / "test_concept_parity.py"] = (TESTS_CONCEPT_PARITY, True)

    files.update(
        {
            root / path: (content, False)
            for path, content in render_spec_files(ctx).items()
        }
    )

    selected_templates = {
        value: name
        for name, value in globals().items()
        if name
        in {
            "DOCKERFILE",
            "DEBUG_DOCKERFILE",
            "BUMPVERSION_CFG",
            "README_MD",
            "DOCS_INDEX_MD",
            "DOCS_OVERVIEW_MD",
            "DOCS_INSTALLATION_MD",
            "DOCS_DEPLOYMENT_MD",
            "DOCS_USAGE_MD",
            "DOCS_PLATFORM_MD",
            "ROOT_AGENTS_MD",
            "CHANGELOG_MD",
            "MKDOCS_YML",
            "ENV_EXAMPLE",
            "ROOT_MCP_CONFIG_JSON",
            "MCP_COMPOSE_YML",
            "AGENT_COMPOSE_YML",
            "PYPROJECT_TOML",
            "INIT_PY",
        }
    }

    # ── Write all files ──────────────────────────────────────────────────
    for path, (template, needs_format) in files.items():
        template_name = selected_templates.get(template, "")
        selected = select_template(template_name, template, has_agent)
        selected = select_backend_template(template_name, selected, backend)
        content = selected.format(**ctx) if needs_format else selected
        if _write_generated_text(path, content):
            print(f"  ✅ {path.relative_to(root.parent)}")

    with staged_theme_files() as theme_files:
        validate_theme_destinations(root, (relative for _, relative in theme_files))
        for source, relative in theme_files:
            _copy_generated_file(source, root / relative)
    check_shared_theme(root)

    # Bundled validation scripts; integration parity uses the actual generated client.
    for script_name in (
        "security_sanitizer.py",
        "verify_api_integration.py",
        "validate_a2a_agent.py",
        # Cross-platform import-safety gate (2026-08-13 Windows-coverage
        # program): walks every module in the scaffolded package and fails
        # on ImportError, with --simulate-windows poisoning fcntl/termios/
        # pwd/resource via sys.modules so a POSIX dev machine catches the
        # "unconditional top-level import of a POSIX-only stdlib module"
        # defect class before Windows CI does. Stdlib-only, no dependency
        # to add. See its own docstring for the documented sys.platform
        # false-positive limitation. Wired into .pre-commit-config.yaml's
        # check-import-safety hook below.
        "check_import_safety.py",
        # Structural scanner dispatcher.  It is copied as a single, standard
        # library-only helper so each generated package owns the same
        # fail-closed staged/delta semantics without hook-time installation.
    ):
        if script_name == "validate_a2a_agent.py" and not has_agent:
            continue
        if script_name == "verify_api_integration.py" and backend != "api_client":
            continue
        src = TEMPLATES_DIR / script_name
        dst = root / "scripts" / script_name
        if src.is_file():
            if _copy_generated_file(src, dst):
                print(f"  ✅ {dst.relative_to(root.parent)} (bundled golden script)")
        else:
            print(
                f"  ⚠️  {script_name} template missing — copy it from "
                "the installed mcp-builder resources"
            )

    # Bundled workspace-source drift guard (CONCEPT:OS-5.72-workspace-uv-sources) —
    # sourced from this scaffolder's own scripts/ dir, not templates/, since it is
    # the scaffolder's own tooling, not a per-package golden reference.
    _scaffolder_scripts_dir = Path(__file__).resolve().parent
    for script_name in ("bootstrap_environment.py", "bootstrap_sources.py"):
        _copy_generated_file(
            _scaffolder_scripts_dir / script_name, root / "scripts" / script_name
        )
    for script_name in (
        "workspace_sources.py",
        "check_workspace_source_drift.py",
        "check_connector_contract.py",
    ):
        src = _scaffolder_scripts_dir / script_name
        dst = root / "scripts" / script_name
        if src.is_file():
            if _copy_generated_file(src, dst):
                print(
                    f"  ✅ {dst.relative_to(root.parent)} (bundled workspace-source guard)"
                )

    # Documentation readiness is a builder-owned contract.  Copy the exact
    # generator/schema pair so every package inherits the same deterministic,
    # source-only and privacy-safe implementation.
    readiness_script = _scaffolder_scripts_dir / "agent_readiness.py"
    readiness_schema = _scaffolder_scripts_dir / "agent_readiness_schema.json"
    readiness_tck = _scaffolder_scripts_dir / "agent_readiness_tck.py"
    if (
        not readiness_script.is_file()
        or not readiness_schema.is_file()
        or not readiness_tck.is_file()
    ):
        raise FileNotFoundError("agent-readiness builder contract is incomplete")
    readiness_outputs = (
        (readiness_script, root / "scripts" / "generate_agent_readiness.py"),
        (readiness_schema, root / "docs" / "agent-readiness.schema.json"),
        (readiness_tck, root / "scripts" / "agent_readiness_tck.py"),
    )
    for source, destination in readiness_outputs:
        if _copy_generated_file(source, destination):
            print(f"  ✅ {destination.relative_to(root.parent)}")

    # Generate current discovery artifacts only after all source pages and the
    # explicit applicability input exist.  This calls the same reviewed
    # function copied into the package and does not import provider code.
    script_dir_text = str(_scaffolder_scripts_dir)
    if script_dir_text not in sys.path:
        sys.path.insert(0, script_dir_text)
    from agent_readiness import generate as generate_readiness

    generate_readiness(root, applicability=root / "docs" / "agent-readiness.json")
    print(
        f"  ✅ {(root / 'llms.txt').relative_to(root.parent)} (agent-readiness index)"
    )

    # requirements.txt mirrors [project].dependencies
    import tomllib

    pyproject_content = (root / "pyproject.toml").read_text(encoding="utf-8")
    parsed_toml = tomllib.loads(pyproject_content)
    deps = parsed_toml.get("project", {}).get("dependencies", [])

    req_path = root / "requirements.txt"
    if _write_generated_text(req_path, "\n".join(deps) + "\n"):
        print(f"  ✅ {req_path.relative_to(root.parent)}")

    print(f"\n🎉 Scaffolded '{package_name}' at {root.resolve()}")
    print(f"   Package dir: {pkg_dir}/")
    commands = [mcp_cmd] + ([agent_cmd] if "agent" in types else [])
    print(f"   Console scripts: {', '.join(commands)}")
    print(f"   Concept prefix: CONCEPT:{concept_prefix}-*")
    print(f"   Types: {', '.join(types)}")
    print("   → Run `uv lock` to generate uv.lock (required by the pre-commit gate).")
    print(
        "   → Run `python scripts/generate_tool_schemas.py` before the first contract check."
    )
    if doc_urls:
        print(f"   Doc URLs saved: {doc_urls}")
        print("   → Run skill-graph-builder to generate docs skill.")


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scaffold a complete agent-package project using the connector SDK and shared pipelines contracts."
    )
    parser.add_argument(
        "package_name",
        help="Kebab-case package name (e.g., 'jellyfin-mcp', 'my-service-mcp')",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Parent directory for the new project (default: current dir)",
    )
    parser.add_argument(
        "--type",
        default="api_client,mcp",
        dest="pkg_types",
        type=str,
        help="Required: api_client,mcp or cli,mcp; optional: agent; graphql requires api_client (default: api_client,mcp)",
    )
    parser.add_argument(
        "--display-name",
        default="",
        help="Human-readable display name (default: derived from package name)",
    )
    parser.add_argument(
        "--description",
        default="",
        help="One-line description (default: auto-generated)",
    )
    parser.add_argument(
        "--concept-prefix",
        default="",
        help="Unique CONCEPT ID prefix (default: derived from package name; check the registry in SKILL.md for collisions)",
    )
    parser.add_argument(
        "--doc-urls",
        default="",
        help="Comma-separated documentation URLs for skill-graph generation",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        default=False,
        help="Write files directly into --output-dir instead of creating a subdirectory",
    )

    parser.add_argument(
        "--generation-date",
        dest="generated_on",
        help="ISO generation date; defaults to SOURCE_DATE_EPOCH or today in UTC, never a delivery date",
    )

    args = parser.parse_args()
    scaffold(
        package_name=args.package_name,
        output_dir=args.output_dir,
        pkg_types=args.pkg_types,
        display_name=args.display_name,
        description=args.description,
        concept_prefix=args.concept_prefix,
        doc_urls=args.doc_urls,
        in_place=args.in_place,
        generated_on=args.generated_on,
    )
