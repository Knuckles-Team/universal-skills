#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Package Builder — Scaffolds a complete agent-package project.

Generates the full project structure following the gitlab-api golden standard
(/home/apps/workspace/agent-packages/agents/gitlab-api), including the modular
api/ and mcp/ split, the full pre-commit gate, the three GitHub workflows
(pipeline/docs/pages), the 7-page Material mkdocs site, AGENTS.md+CLAUDE.md
stub pattern, and the a2a.json / opencode.json / pytest.ini / MANIFEST.in /
.codespellignore / .vulture_ignore config set.

See PARITY_MANIFEST.md (sibling of SKILL.md) for the definitive checklist.
"""

import argparse
import datetime
import shutil
from pathlib import Path

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


# ── Templates (golden standard: gitlab-api) ──────────────────────────────────
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
requires-python = ">=3.11, <3.15"
dependencies = [ "agent-utilities>=0.51.0", "python-dotenv>=1.0.0",{gql_core_dep}]
[[project.authors]]
name = "{author}"
email = "{email}"

[project.license]
text = "MIT"

[project.optional-dependencies]
mcp = [ "agent-utilities[mcp]>=0.51.0",]
agent = [ "agent-utilities[agent,logfire]>=0.51.0",]
{gql_extra}all = [ "{package_name}[{all_extras}]>=0.1.0",]
test = [
    "pytest-xdist>=3.6.0", "pytest", "pytest-asyncio", "pytest-cov",]

[project.scripts]
{mcp_cmd} = "{pkg_dir}.mcp_server:mcp_server"
{agent_cmd} = "{pkg_dir}.agent_server:agent_server"

[tool.setuptools]
include-package-data = true

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.mypy]
python_version = "3.10"
ignore_missing_imports = true
check_untyped_defs = true

[dependency-groups]
dev = [
    "pytest-timeout>=2.4.0",
]

[tool.setuptools.package-data]
{pkg_dir} = [ "mcp_config.json", "agent_data/**",]

[tool.ruff.lint]
select = [ "E", "F", "I", "UP", "B",]
ignore = [ "E402", "E501", "B008",]

[tool.setuptools.packages.find]
where = [ ".",]

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

[bumpversion:file(all-extra):pyproject.toml]
search = {package_name}[{all_extras}]>={{current_version}}
replace = {package_name}[{all_extras}]>={{new_version}}

[bumpversion:file:a2a.json]
search = "version": "{{current_version}}"
replace = "version": "{{new_version}}"

[bumpversion:file:README.md]
search = Version: {{current_version}}
replace = Version: {{new_version}}

[bumpversion:file:docker/Dockerfile]
search = {package_name}[all]>={{current_version}}
replace = {package_name}[all]>={{new_version}}

[bumpversion:file:{pkg_dir}/agent_server.py]
search = __version__ = "{{current_version}}"
replace = __version__ = "{{new_version}}"

[bumpversion:file:{pkg_dir}/mcp_server.py]
search = __version__ = "{{current_version}}"
replace = __version__ = "{{new_version}}"
"""

# Verbatim golden gitlab-api pre-commit gate (no format placeholders — the
# bash one-liners contain literal braces).
PRECOMMIT_CONFIG = """\
default_language_version:
  python: python3
exclude: 'dotnet|node_modules'
ci:
  autofix_prs: true
  autoupdate_commit_msg: '[pre-commit.ci] pre-commit suggestions'
  autoupdate_schedule: 'monthly'

repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v6.0.0
  hooks:
  - id: check-added-large-files
    args: ["--maxkb=2000"]
  - id: check-ast
    exclude: ^(tests/|test/|scripts/|script/)
  - id: check-yaml
    args: ["--unsafe"]
  - id: check-toml
  - id: check-json
  - id: fix-byte-order-marker
    exclude: .gitignore
  - id: check-merge-conflict
  - id: detect-private-key
  - id: trailing-whitespace
  - id: end-of-file-fixer
  - id: no-commit-to-branch
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.15.12
  hooks:
  - id: ruff-check
    args: ["--fix", "--ignore=E402,B008,E501"]
    exclude: ^(tests/|test/|scripts/|script/)
  - id: ruff-format
    exclude: ^(tests/|test/|scripts/|script/)
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.20.2
  hooks:
  - id: mypy
    additional_dependencies: [pydantic, types-PyYAML, types-requests,
        types-setuptools]
    args: ["--ignore-missing-imports"]
- repo: https://github.com/jendrikseipp/vulture
  rev: v2.16
  hooks:
  - id: vulture
    pass_filenames: false
    args: [".", "--min-confidence", "95", "--exclude", "node_modules,dotnet,.venv"]
    require_serial: true
- repo: https://github.com/codespell-project/codespell
  rev: v2.4.2
  hooks:
  - id: codespell
    args: ["-L", "ans,linar,nam,tread,ot,", "--ignore-words=.codespellignore"]
    exclude: ^(tests/|test/|scripts/|script/|.*lock.*)
- repo: https://github.com/PyCQA/bandit
  rev: 1.9.4
  hooks:
  - id: bandit
    args: ["--skip", "B101,B404,B603"]
    exclude: ^(tests/|test/|scripts/|script/|__tests__/)
- repo: https://github.com/nbQA-dev/nbQA
  rev: 1.9.1
  hooks:
  - id: nbqa-ruff
    args: ["--fix"]
- repo: https://github.com/astral-sh/uv-pre-commit
  rev: 0.11.8
  hooks:
  - id: uv-lock
- repo: local
  hooks:
  - id: check-mermaid
    name: Check Mermaid syntax
    entry: python3 /home/apps/workspace/agent-packages/agent-utilities/scripts/mermaid_linter.py
    language: system
    files: \\.md$
    pass_filenames: true
  - id: check-stubs
    name: Check for Active Stubs and TODOs
    entry: python3 /home/apps/workspace/agent-packages/agent-utilities/scripts/check_stubs.py
    language: system
    types: [python]
  - id: mermaid-validate
    name: mermaid-validate
    entry: mermaid-validate
    language: node
    additional_dependencies: ['@zabaca/mermaid-validate@1.0.1']
    types: [markdown]
    pass_filenames: true
  - id: check-agent-standards
    name: check agent standards
    entry: |-
      bash -c 'for f in $(find . -type f -name "agent_server.py" -not -path "*/\\.venv/*" -not -path "*/__pycache__/*"); do grep -q "warnings.filterwarnings" "$f" && grep -q "file=sys.stderr" "$f" || { echo "Missing warnings.filterwarnings or file=sys.stderr in $f"; exit 1; }; done'
    language: system
    pass_filenames: false
    always_run: true
  - id: check-cli-help
    name: check cli help
    entry: |-
      bash -c 'for f in $(find . -type f \\( -name "mcp_server.py" -o -name "agent_server.py" \\) -not -path "*/\\.venv/*" -not -path "*/__pycache__/*"); do mod=$(echo "$f" | sed -e "s/^\\.\\///" -e "s/\\.py$//" -e "s/\\//./g"); uv run python -m "$mod" --help >/dev/null || exit 1; done'
    language: system
    pass_filenames: false
    always_run: true
  - id: check-bumpversion
    name: validate bumpversion config
    entry: |-
      bash -c 'if [ -f ".bumpversion.cfg" ]; then bump2version patch --dry-run --allow-dirty; fi'
    language: system
    pass_filenames: false
    always_run: true
- repo: local
  hooks:
  - id: pytest
    name: pytest
    entry: bash -c 'test_target="tests"; for d in tests/unit test/unit tests test; do if [ -d "$d" ]; then test_target="$d"; break; fi; done; if [ -f uv.lock ]; then uv run --all-extras pytest "$test_target" -q --tb=short -m "not slow" --timeout=60; else pytest "$test_target" -q --tb=short -m "not slow" --timeout=60; fi'
    language: system
    types: [python]
    pass_filenames: false
    always_run: true
- repo: https://github.com/AleksaC/hadolint-py
  rev: v2.14.0
  hooks:
  - id: hadolint
    args:
    - --ignore=DL3008
    - --ignore=DL3015
    - --ignore=DL3009
    - --ignore=DL4006
    - --ignore=SC2102
- repo: https://github.com/IamTheFij/docker-pre-commit
  rev: v3.0.1
  hooks:
  - id: docker-compose-check

- repo: local
  hooks:
  - id: verify-api-integration
    name: Verify API-to-MCP Integration Coverage
    entry: python scripts/verify_api_integration.py --local
    language: system
    pass_filenames: false
    always_run: true
- repo: local
  hooks:
  - id: security-sanitizer
    name: Security and Garbage Sanitizer
    entry: python scripts/security_sanitizer.py
    language: python
    pass_filenames: false
    always_run: true
"""

DOCKERFILE = """\
# syntax=docker/dockerfile:1
# Slim multi-stage build: install in a builder, ship only /usr/local. Cuts the
# pushed image ~43% (no default-jre/dev-tools/source) so layer pushes finish well
# inside the registry's blob-upload window even under concurrency.
FROM python:3.11-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \\
    UV_LINK_MODE=copy \\
    UV_SYSTEM_PYTHON=1 \\
    UV_HTTP_TIMEOUT=3600
# Some [all] deps (e.g. hnswlib, an agent-utilities transitive) ship no manylinux
# wheel and build from sdist, needing a C++ toolchain. Install it in the builder
# only — the final stage copies just /usr/local, so no compiler ships.
RUN apt-get update \\
    && apt-get install -y --no-install-recommends build-essential \\
    && rm -rf /var/lib/apt/lists/*
RUN --mount=type=cache,target=/root/.cache/uv \\
    uv pip install --system --upgrade --break-system-packages --prerelease=allow {package_name}[all]>=0.1.0

FROM python:3.11-slim

ARG HOST=0.0.0.0
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

# Install base dependencies, uv, and starship shell prompt
COPY --from=builder /usr/local /usr/local

CMD ["{mcp_cmd}"]
"""

DEBUG_DOCKERFILE = """\
FROM python:3.11-slim

ARG HOST=0.0.0.0
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
    UV_COMPILE_BYTECODE=1 \\
    RUSTUP_HOME="/usr/local/rustup" \\
    CARGO_HOME="/usr/local/cargo"

# Install base dependencies, uv, and starship shell prompt
RUN apt-get update \\
    && apt-get install -y default-jre ripgrep tree fd-find curl nano build-essential cmake libssl-dev libcurl4-openssl-dev pkg-config \\
    && curl -LsSf https://astral.sh/uv/install.sh | sh \\
    && curl -sS https://starship.rs/install.sh | sh -s -- --yes \\
    && curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable --profile minimal \\
    && mkdir -p /root/.config \\
    && echo "eval \\"\\$(starship init bash)\\"" >> /root/.bashrc \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Compile and install package in-place
RUN uv pip install --system --upgrade --verbose --no-cache --break-system-packages --prerelease=allow .[all]

COPY docker/starship.toml /root/.config/starship.toml

CMD ["{mcp_cmd}"]
"""

AGENT_COMPOSE_YML = """\
version: '3.8'

services:
  {package_name}-mcp:
    image: knucklessg1/{package_name}:latest
    container_name: {package_name}-mcp
    hostname: {package_name}-mcp
    restart: always
    env_file:
      - ../.env
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
    ports:
      - "8000:8000"
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
    image: knucklessg1/{package_name}:latest
    container_name: {package_name}-agent
    hostname: {package_name}-agent
    restart: always
    depends_on:
      - {package_name}-mcp
    env_file:
      - ../.env
    command: [ "{agent_cmd}" ]
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT={agent_port}
      - MCP_URL=http://{package_name}-mcp:8000/mcp
      - PROVIDER=${{PROVIDER:-openai}}
      - MODEL_ID=${{MODEL_ID:-gpt-4o}}
      - ENABLE_WEB_UI=True
      - ENABLE_OTEL=True
    ports:
      - "{agent_port}:{agent_port}"
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
    image: knucklessg1/{package_name}:latest
    container_name: {package_name}-mcp
    hostname: {package_name}-mcp
    restart: always
    env_file:
      - ../.env
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
    ports:
      - "8000:8000"
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
# ==============================================================================
# {display_name} Environment Configuration
# ==============================================================================

# --- MCP Server Settings ---
HOST=0.0.0.0
PORT=8000
TRANSPORT=stdio # options: stdio, streamable-http, sse

# --- Telemetry & Observability (OTEL / Langfuse) ---
ENABLE_OTEL=True
# OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:8080/api/public/otel
# OTEL_EXPORTER_OTLP_PUBLIC_KEY=pk-...
# OTEL_EXPORTER_OTLP_SECRET_KEY=sk-...
# OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf

# --- Enterprise Security & Access Governance (Eunomia) ---
EUNOMIA_TYPE=none # options: none, embedded, remote
EUNOMIA_POLICY_FILE=mcp_policies.json
# EUNOMIA_REMOTE_URL=http://eunomia-server:8000

# --- Core API / Client Credentials for {display_name} ---
{service_url_env}=http://localhost:8080
# {auth_env}=your_token_here

# --- Tool Toggle Switches ---
SYSTEMTOOL=True
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
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "lmstudio": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LM Studio (local)",
      "options": {
        "baseURL": "http://vllm.arpa/v1"
      },
      "models": {
        "qwen/qwen3.5-9b": {
          "name": "Qwen 3.5-9B"
        }
      }
    }
  },
  "model": "lmstudio/qwen/qwen3.5-9b"
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

Copyright (c) {year} {author}

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
recursive-include {pkg_dir} *.py *.json
"""

GITIGNORE = """\
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[codz]
*$py.class

/.ruff_cache/
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
## CLI or API | MCP | Agent

![PyPI - Version](https://img.shields.io/pypi/v/{package_name})
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![PyPI - Downloads](https://img.shields.io/pypi/dd/{package_name})
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/{package_name})
![PyPI - License](https://img.shields.io/pypi/l/{package_name})
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/{package_name})

*Version: 0.1.0*

> **Documentation** — Installation, deployment, usage across the API, CLI, and MCP
> interfaces, the integrated A2A agent server, and guidance for provisioning the
> backing platform are maintained in the
> [official documentation](https://knuckles-team.github.io/{package_name}/).

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Available MCP Tools](#available-mcp-tools)
- [Installation](#installation)
- [Usage](#usage)
- [MCP](#mcp)
- [Documentation](#documentation)

---

## Overview

**{display_name} MCP Server + A2A Agent**

{description}

This repository is actively maintained - Contributions are welcome!

## Key Features

- **Action-routed MCP tools** — each domain is exposed as a single MCP tool that routes
  to many underlying operations via an `action` argument, keeping the tool surface small.
- **Three interfaces, one package** — use it as a Python **API client**, an **MCP server**
  (`stdio` / `streamable-http` / `sse`), or a Pydantic-AI **A2A agent**.
- **`agent-utilities` native** — built on the shared framework (auth, action router,
  telemetry, governance) for fleet consistency.
- **Per-tool toggles** — enable or disable each tool domain with environment switches.
- **Enterprise-ready** — OTEL/Langfuse telemetry and optional Eunomia access governance.

## Available MCP Tools

Each tool is **action-routed**: pass an `action` and a JSON `params_json` payload. Tool
domains can be toggled on or off with the listed environment variable.

| Tool | Toggle env var | Default | Actions |
|------|----------------|:-------:|---------|
| `system_operations` | `SYSTEMTOOL` | `True` | `status`, `info` |

## Installation

### Install with `uvx` (no install — run on demand)

```bash
uvx --from {package_name} {mcp_cmd}      # MCP server
uvx --from {package_name} {agent_cmd}    # A2A agent server
```

### Install with `pip`

```bash
python -m pip install {package_name}            # core (API client)
python -m pip install "{package_name}[all]"     # + MCP server + A2A agent + telemetry
```

### Console scripts

After installation the following entry points are available on your `PATH`:

| Command | Description |
|---------|-------------|
| `{mcp_cmd}` | Launch the MCP server |
| `{agent_cmd}` | Launch the A2A agent server |

## Usage

### As a Python API client

```python
from {pkg_dir}.auth import get_client

client = get_client()
status = client.get_system_status()
print(status)
```

### As an MCP server (CLI)

```bash
# Local stdio (for IDEs)
{mcp_cmd}

# Networked streamable-http
{mcp_cmd} --transport streamable-http --host 0.0.0.0 --port 8000
```

### Calling an MCP tool

Tools are action-routed — pass an `action` plus a JSON `params_json` string:

```json
{{
  "tool": "system_operations",
  "arguments": {{
    "action": "status",
    "params_json": "{{}}"
  }}
}}
```

## MCP

### Using as an MCP Server

The MCP Server can be run in `stdio` (local), `streamable-http` (networked), or
`sse` mode.

#### Environment Variables

*   `{service_url_env}`: The URL of the target service.
*   `{auth_env}`: The API token or access token.

#### stdio Transport (local IDEs — Cursor, Claude Desktop, VS Code)

```json
{{
  "mcpServers": {{
    "{mcp_cmd}": {{
      "command": "uvx",
      "args": ["--from", "{package_name}", "{mcp_cmd}"],
      "env": {{
        "{service_url_env}": "https://service.example.com",
        "{auth_env}": "your_token"
      }}
    }}
  }}
}}
```

#### Streamable-HTTP Transport (networked / production)

```json
{{
  "mcpServers": {{
    "{mcp_cmd}": {{
      "command": "uvx",
      "args": ["--from", "{package_name}", "{mcp_cmd}", "--transport", "streamable-http", "--port", "8000"],
      "env": {{
        "TRANSPORT": "streamable-http",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "{service_url_env}": "https://service.example.com",
        "{auth_env}": "your_token"
      }}
    }}
  }}
}}
```

<!-- BEGIN GENERATED: additional-deployment-options -->
### Additional Deployment Options

`{package_name}` can also run as a **local container** (Docker / Podman / `uv`) or be
consumed from a **remote deployment**. The
[Deployment guide](https://knuckles-team.github.io/{package_name}/deployment/) has full,
copy-paste `mcp_config.json` for all four transports — **stdio**, **streamable-http**,
**local container / uv**, and **remote URL**:

- **Local container / uv** — launch the server from `mcp_config.json` via `uvx`,
  `docker run`, or `podman run`, or point at a local streamable-http container by `url`.
- **Remote URL** — connect to a server deployed behind Caddy at
  `http://{mcp_cmd}.arpa/mcp` using the `"url"` key.
<!-- END GENERATED: additional-deployment-options -->

## Install Python Package

```bash
python -m pip install {package_name}
```

## Documentation

Full documentation is published to the GitHub Pages site and mirrored under `docs/`:

- [Documentation site](https://knuckles-team.github.io/{package_name}/)
- [Overview](docs/overview.md)
- [Installation](docs/installation.md)
- [Usage](docs/usage.md)
- [Deployment](docs/deployment.md)
- [Platform](docs/platform.md)
- [Concept Registry](docs/concepts.md)
"""

CHANGELOG_MD = """\
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - {date}

### Added
- Initial release.
- Modular subfolders for API wrappers (`api/`) and action-routed MCP tools (`mcp/`).
- Material-theme mkdocs documentation site (7 standard pages).
- Full pre-commit quality gate and flat `tests/` structure.
"""

# ── GitHub workflows (golden verbatim) ───────────────────────────────────────

PIPELINE_YML = """\
name: Build|Upload|Release Python Package

on:
  push:
    branches:
      - 'main'

jobs:
  publish-pypi:
    uses: Knuckles-Team/pipelines/.github/workflows/python_pipeline.yml@main
    secrets:
      PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
  publish-docker:
    needs: publish-pypi
    uses: Knuckles-Team/pipelines/.github/workflows/container_pipeline.yml@main
    secrets:
      DOCKER_REGISTRY: ${{ secrets.DOCKER_REGISTRY }}
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
      DOCKER_REPOSITORY: ${{ secrets.DOCKER_REPOSITORY }}
"""

DOCS_YML = """\
name: Deploy Documentation

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  deploy-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install MkDocs
        run: pip install mkdocs-material

      - name: Build and Deploy
        run: mkdocs gh-deploy --force
"""

PAGES_YML = """\
name: Deploy GitHub Pages

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - 'README.md'

jobs:
  publish-pages:
    uses: Knuckles-Team/pipelines/.github/workflows/pages_pipeline.yml@main
"""

# ── AGENTS.md (golden pattern, incl. Quality Bar + worktree sections) ─────────

ROOT_AGENTS_MD = """\
# AGENTS.md

> Claude Code loads this file via `CLAUDE.md` (`@AGENTS.md` import) — the two stay
> in sync. Edit **this** file, not `CLAUDE.md`.

## Tech Stack & Architecture
- Language/Version: Python 3.11+
- Core Libraries: `agent-utilities`, `fastmcp`, `pydantic-ai`
- Key principles: Functional patterns, Pydantic for data validation, asynchronous tool execution.
- Architecture:
    - `{pkg_dir}/api/`: Modular folder for target service client wrappers.
    - `{pkg_dir}/mcp/`: Modular folder for action-routed dynamic MCP tool tags.
    - `{pkg_dir}/mcp_server.py`: Main MCP server entry point and tool registration.
    - `{pkg_dir}/agent_server.py`: Pydantic AI agent definition and logic.

### Architecture Diagram
```mermaid
graph TD
    User([User/A2A]) --> Server[A2A Server / FastAPI]
    Server --> Agent[Pydantic AI Agent]
    Agent --> Skills[Modular Skills]
    Agent --> MCP[MCP Server / FastMCP]
    MCP --> Client[API Client / Wrapper]
    Client --> ExternalAPI([External Service API])
```

### Workflow Diagram
```mermaid
sequenceDiagram
    participant U as User
    participant S as Server
    participant A as Agent
    participant T as MCP Tool
    participant API as External API

    U->>S: Request
    S->>A: Process Query
    A->>T: Invoke Tool
    T->>API: API Request
    API-->>T: API Response
    T-->>A: Tool Result
    A-->>S: Final Response
    S-->>U: Output
```

## Commands (run these exactly)
# Installation
pip install .[all]

# Quality & Linting (run from project root)
pre-commit run --all-files

# Execution Commands
# Run MCP Server
{mcp_cmd}
# Run Agent
{agent_cmd}

## Project Structure Quick Reference
- MCP Entry Point → `{pkg_dir}/mcp_server.py`
- Agent Entry Point → `{pkg_dir}/agent_server.py`
- Source Code → `{pkg_dir}/`
- API client mixins → `{pkg_dir}/api/`
- MCP tool modules → `{pkg_dir}/mcp/`
- Tests → `tests/`
- Documentation → `docs/` (published via mkdocs + GitHub Pages)

## Code Style & Conventions
**Always:**
- Use `agent-utilities` for common patterns (e.g., `create_mcp_server`, `create_agent_server`).
- Define input/output models using Pydantic.
- Include descriptive docstrings for all tools (they are used as tool descriptions for LLMs).
- Check for optional dependencies using `try/except ImportError`.

## Dos and Don'ts
**Do:**
- Run `pre-commit` before pushing changes.
- Use existing patterns from `agent-utilities`.
- Keep tools focused and idempotent where possible.

**Don't:**
- Use `cd` commands in scripts; use absolute paths or relative to project root.
- Add new dependencies to `dependencies` in `pyproject.toml` without checking `optional-dependencies` first.
- Hardcode secrets; use environment variables or `.env` files.

## Safety & Boundaries
**Always do:**
- Run lint/test via `pre-commit`.
- Use `agent-utilities` base classes.

**Ask first:**
- Major refactors of `mcp_server.py` or `agent_server.py`.
- Deleting or renaming public tool functions.

**Never do:**
- Commit `.env` files or secrets.
- Modify `agent-utilities` or `universal-skills` files from within this package.

## When Stuck
- Propose a plan first before making large changes.
- Check `agent-utilities` documentation for existing helpers.

## ⛔ No Scratch or Temporary Files in Repository

**NEVER write any of the following to this repository:**
- Temporary test scripts (`test_*.py`, `debug_*.py` outside of `tests/`)
- Scratch scripts or experimental one-off files
- Log files (`.log`, `.txt` command output)
- Random text files with command output or debug dumps
- Any file that is NOT production source code, tests in `tests/`, or documentation

**Why:** These files expose private filesystem paths, credentials, and internal infrastructure details when pushed to GitHub publicly.

**Where to put scratch work instead:**
- Use `~/workspace/scratch/` for temporary scripts and experiments
- Use `~/workspace/reports/` for command output and reports
- Keep test scripts in the `tests/` directory following proper pytest conventions

## ⛔ Keep the Repository Root Pristine — No Scratch / Temp / Debug Files

**The repository ROOT must contain only canonical project files** (packaging,
config, docs, lockfiles). The only hidden directories allowed at root are
`.git/`, `.github/`, and `.specify/` (plus a local, git-ignored `.venv/`).

**NEVER write any of the following — anywhere in the repo, and ESPECIALLY at the root:**
- One-off / debug / migration scripts: `fix_*.py`, `migrate_*.py`, `refactor_*.py`,
  `replace_*.py`, `update_*.py`, `debug_*.py`, or `test_*.py` **at the root**
  (real tests live in `tests/` only).
- Databases / data dumps: `*.db`, `*.db-wal`, `*.sqlite*`, `*.corrupted`.
- Logs / command output: `*.log`, scratch `*.txt`, `*.orig`, `*.rej`, `*.bak`.
- Build artifacts: `*.tsbuildinfo`, compiled binaries, coverage files.
- AI agent scratch directories: `.agent/`, `.agents/`, `.agent_data/`, `.tmp/`,
  `.hypothesis/`, or any per-tool cache committed to git.
- Any file that is NOT production source, a test in `tests/`, documentation, or
  a recognized config/lockfile.

**Why:** scratch at the root leaks private paths/credentials, bloats the tree,
and erodes a pristine codebase.

**Where scratch goes instead:** `~/workspace/scratch/` (experiments),
`~/workspace/reports/` (command output); tests go in `tests/` (pytest).
Before finishing a task, run `git status` and confirm no stray root files were added.

## Working Discipline — think, simplify, stay surgical, verify

These four habits cut the most common LLM coding mistakes. For trivial tasks, use
judgment; the bias here is correctness over speed.

- **Think before coding.** State your assumptions explicitly. If a request has more than
  one reasonable reading, surface the options instead of silently picking one. If a
  simpler approach exists, say so and push back when warranted. When something is
  genuinely unclear, stop and name what's confusing — ask, don't guess.
- **Simplicity first.** Write the minimum code that solves the stated problem — no
  speculative features, no abstraction for single-use code, no configurability that
  wasn't requested, no error handling for impossible states. If you wrote 200 lines and
  it could be 50, rewrite it. (Name code from its purpose, never `wave0`/`phase2`/`v2`.)
- **Stay surgical.** Every changed line should trace directly to the task. Don't refactor,
  reformat, or "improve" working code adjacent to your change; match the existing style
  even where you'd do it differently. Remove only the imports/symbols your own change
  orphaned; if you spot unrelated dead code, mention it rather than deleting it inline.
  *Exception — the Quality Bar below:* lint/format/type errors the pre-commit gate flags
  get fixed regardless of who introduced them. In short: **surgical on behavior, clean on
  lint.**
- **Verify against a goal.** Turn the task into a checkable outcome before you start:
  "fix the bug" → "write a failing test that reproduces it, then make it pass"; "add
  validation" → "tests for the invalid inputs pass". For multi-step work, state the short
  plan and the check for each step, then loop until the checks pass.

## Quality Bar — Leave the Codebase Clean (REQUIRED)

After completing any code change, run the project's pre-commit suite and drive it
**fully green** before committing:

```bash
pre-commit run --all-files
```

Resolve **every** issue it reports — failures, lint errors, type errors, and
warnings — **including problems that pre-date your change and were not caused by
your edits**. The standing goal is a clean, working codebase with **no errors and
no warnings**. Do not silence checks (`# noqa`, `# type: ignore`, `SKIP=`,
`--no-verify`) to force green unless the exception is already documented in this
file as a known, unavoidable limitation. Only commit once `pre-commit run
--all-files` passes cleanly; if a check legitimately cannot pass, stop and explain
why rather than bypassing it.

## Working with Git Worktrees (multi-session)

Multiple agents/sessions work the `agent-packages/*` repos concurrently. **Do not
edit the canonical checkout** (`/home/apps/workspace/agent-packages/<repo>`) — a
background `repository-manager` sync can reset its working tree and discard
uncommitted edits. Take your own git worktree on your own branch instead:

```bash
# preferred — repository-manager MCP:
rm_worktree add <repo> <your-branch>      # -> /home/apps/worktrees/<repo>/<your-branch>

# raw-git fallback:
git -C agent-packages/<repo> checkout main
git -C agent-packages/<repo> worktree add /home/apps/worktrees/<repo>/<branch> -b <branch>
```

Work in the worktree and **commit often** (commits survive a working-tree reset).
Each session must use a **distinct branch** — git allows a branch in only one
worktree, which is what keeps concurrent sessions from colliding. Worktrees live
under `/home/apps/worktrees/` (outside the workspace scan, so the sync leaves them
alone).

**Finishing work in a worktree** — run this sequence before calling it done:
1. **Pre-commit green** — `pre-commit run --all-files`; resolve every issue per the
   Quality Bar above (including pre-existing), no `--no-verify`.
2. **Commit** in the worktree.
3. **Merge to main locally** — `rm_worktree merge <repo> <branch> --into main`
   (or `git merge --no-ff`). Push only when the user asks.
4. **Clean up** — remove the worktree and delete the merged branch:
   `rm_worktree remove <repo> <branch> --delete-branch`; `rm_worktree prune` clears
   stale entries. (Raw-git: `git worktree remove <path> && git branch -d <branch>`.)
"""

# ── Package source templates ─────────────────────────────────────────────────

INIT_PY = """\
#!/usr/bin/env python
# coding: utf-8

import importlib
import inspect
import warnings
from typing import List

warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")

__all__: List[str] = []

CORE_MODULES = [
    "{pkg_dir}.api",
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

AUTH_PY = """\
#!/usr/bin/python

\"\"\"Authentication.

Priority:
1. **OIDC Delegation** (RFC 8693 Token Exchange) — when ``ENABLE_DELEGATION`` is
   active, exchanges the IdP-issued user token for a downstream access token via the
   shared ``agent_utilities.mcp.delegated_auth`` helper.
2. **Fixed credentials** — falls back to the ``{auth_env}`` env var.

For a multi-tenant service, add an ``instances.py`` that resolves a configured
instance NAME (from ``<service>_instances`` in ``~/.config/agent-utilities/config.json``)
to ``(url, token, verify)`` and call it here before the delegation/fixed paths — see
``gitlab_api.instances`` (CONCEPT:KG-2.9g) for the golden pattern.
\"\"\"

from agent_utilities.base_utilities import get_logger
from agent_utilities.core.config import setting
from agent_utilities.core.exceptions import AuthError, UnauthorizedError

from .api import ApiClientSystem

logger = get_logger(__name__)
_client = None


def get_client(
    url: str | None = None,
    token: str | None = None,
    verify: bool | None = None,
    config: dict | None = None,
) -> ApiClientSystem:
    \"\"\"Get or create a singleton API client (OIDC delegation or fixed credentials).

    Credentials resolve through the shared config layer (the one XDG
    ``config.json`` / env) at call time, not frozen at import.
    \"\"\"
    global _client
    if _client is not None:
        return _client

    base_url = url or setting("{service_url_env}", "http://localhost:8080")
    token = token or setting("{auth_env}", "")
    if verify is None:
        verify = setting("{ssl_verify_env}", True)

    from agent_utilities.mcp.delegated_auth import (
        get_delegated_token,
        get_user_identity,
        is_delegation_enabled,
    )

    # --- Path 1: OIDC Delegation (RFC 8693 Token Exchange) ---
    if is_delegation_enabled(config):
        try:
            delegated_token = get_delegated_token(
                config=config,
                audience=(config or {{}}).get("audience", base_url),
                scopes=(config or {{}}).get("delegated_scopes", "api"),
                verify=verify,
            )
            identity = get_user_identity()
            logger.info(
                "Using OIDC delegated token",
                extra={{"user_email": identity.get("email"), "url": base_url}},
            )
            _client = ApiClientSystem(
                base_url=base_url, token=delegated_token, verify=verify
            )
            return _client
        except Exception as e:
            logger.error(
                "OIDC delegation failed",
                extra={{"error_type": type(e).__name__, "error_message": str(e)}},
            )
            raise RuntimeError(f"Token exchange failed: {{str(e)}}") from e

    # --- Path 2: Fixed Credentials ({auth_env}) ---
    logger.info("Using fixed credentials")
    try:
        _client = ApiClientSystem(base_url=base_url, token=token, verify=verify)
    except (AuthError, UnauthorizedError) as e:
        raise RuntimeError(
            f"AUTHENTICATION ERROR: The credentials provided are not valid for '{{base_url}}'. "
            f"Please check your {auth_env} and {service_url_env} environment variables. "
            f"Error details: {{str(e)}}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"AUTHENTICATION ERROR: Failed to instantiate client. "
            f"Error details: {{str(e)}}"
        ) from e

    return _client
"""

MCP_SERVER_PY = """\
#!/usr/bin/python

import logging
import sys
from typing import Any

from agent_utilities.base_utilities import get_logger
from agent_utilities.mcp_utilities import (
    create_mcp_server,
    load_config,
    register_tool_surface,
)

from . import mcp as tool_modules
from .api import ApiClientSystem
from .auth import get_client

__version__ = "0.1.0"

logger = get_logger(name="MCP_Server")
logger.setLevel(logging.INFO)


def get_mcp_instance() -> tuple[Any, Any, Any]:
    \"\"\"Initialize and return the {display_name} MCP instance, args, and middlewares.

    The whole tool surface is wired by the shared ``register_tool_surface`` helper
    per ``MCP_TOOL_MODE`` (read from the XDG config): ``condensed`` (default,
    action-routed tools), ``verbose`` (one named 1:1 tool per API method), or
    ``both``. To add a domain, drop a ``register_<domain>_tools(mcp)`` into the
    ``mcp/`` package and re-export it from ``mcp/__init__.py`` — it is auto-discovered
    and gated by ``setting("<DOMAIN>TOOL", True)``; no edit here is needed. For
    fully-typed verbose tools, vendor an OpenAPI/Swagger spec under ``specs/`` and
    generate ``api/_operation_manifest.py``, then pass ``manifest=OPERATIONS`` below.
    \"\"\"
    load_config()

    args, mcp, middlewares = create_mcp_server(
        name="{display_name} MCP",
        version=__version__,
        instructions="{display_name} MCP Server — condensed and verbose tool surfaces.",
    )

    register_tool_surface(
        mcp,
        service="{package_name}",
        client_cls=ApiClientSystem,
        get_client=get_client,
        tools_module=tool_modules,
    )

    for mw in middlewares:
        mcp.add_middleware(mw)

    return mcp, args, middlewares


def mcp_server():
    mcp, args, _ = get_mcp_instance()

    print(f"{display_name} MCP v{{__version__}}", file=sys.stderr)
    print("\\nStarting MCP Server", file=sys.stderr)
    print(f"  Transport: {{args.transport.upper()}}", file=sys.stderr)

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger.error(f"Invalid transport: {{args.transport}}")
        sys.exit(1)


if __name__ == "__main__":
    mcp_server()
"""

AGENT_SERVER_PY = """\
#!/usr/bin/python
import logging
import os
import sys
import warnings

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
    agent_name = os.getenv("DEFAULT_AGENT_NAME", meta.get("name", "{display_name}"))

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
        api_key=args.api_key,
        agent_description=os.getenv(
            "AGENT_DESCRIPTION", meta.get("description", "{description}")
        ),
        system_prompt=os.getenv(
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

API_CLIENT_FACADE = """\
#!/usr/bin/python
\"\"\"Facade re-export of the modular api/ sub-package (backward compatibility).\"\"\"

from .api import *  # noqa: F401,F403
from .api import __all__ as _api_all

__all__ = list(_api_all)
"""

API_CLIENT_BASE = """\
from typing import Any, Dict

import requests


class ApiClientBase:
    \"\"\"Base HTTP API client wrapper.\"\"\"

    def __init__(self, base_url: str, token: str, verify: bool = True):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.verify = verify
        self.session = requests.Session()
        self.session.headers.update({{"Authorization": f"Bearer {{token}}"}})

    def request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        url = f"{{self.base_url}}/{{path.lstrip('/')}}"
        response = self.session.request(method, url, verify=self.verify, **kwargs)
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return {{"status": response.status_code, "text": response.text}}
"""

API_CLIENT_SYSTEM = """\
from typing import Any, Dict

from .api_client_base import ApiClientBase


class ApiClientSystem(ApiClientBase):
    \"\"\"System status and monitoring API operations.\"\"\"

    def get_system_status(self) -> Dict[str, Any]:
        \"\"\"Retrieve the status of the target system.\"\"\"
        return self.request("GET", "/health")
"""

API_INIT_PY = """\
from .api_client_base import ApiClientBase
from .api_client_system import ApiClientSystem

__all__ = ["ApiClientBase", "ApiClientSystem"]
"""

INPUT_MODELS_PY = """\
#!/usr/bin/python
\"\"\"Pydantic input models for {display_name} API request parameters.\"\"\"

from typing import Optional

from pydantic import BaseModel, Field


class SystemStatusInput(BaseModel):
    \"\"\"Input model for system status queries.\"\"\"

    verbose: Optional[bool] = Field(
        default=False, description="Return extended status details."
    )
"""

RESPONSE_MODELS_PY = """\
#!/usr/bin/python
\"\"\"Pydantic response models for {display_name} API payloads.\"\"\"

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SystemStatusResponse(BaseModel):
    \"\"\"Response model for system status queries.\"\"\"

    status: Optional[str] = Field(default=None, description="Service status string.")
    raw: Optional[Dict[str, Any]] = Field(
        default=None, description="Raw response payload."
    )
"""

MCP_SYSTEM_PY = """\
import json

from agent_utilities.mcp_utilities import resolve_action, run_blocking
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
            return {{"error": f"Invalid params_json: {{e}}"}}

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
        "{service_url_env}": "<YOUR_{service_url_env}>",
        "{auth_env}": "<YOUR_{auth_env}>",
        "{ssl_verify_env}": "<YOUR_{ssl_verify_env}>",
        "SYSTEMTOOL": "True"
      }}
    }}
  }}
}}
"""

MAIN_AGENT_JSON = """\
{
  "task": "main-agent",
  "input": "# main-agent\\n\\nYou are the primary orchestrator for this workspace. Your goal is to help the user manage their projects and coordinate specialized agents.\\n\\n### Core Principles\\n* Be concise and efficient.\\n* Use the knowledge graph to discover tools and experts.\\n* Verify your work before concluding.\\n\\nYour personality:\\n* **Emoji:** 🤖\\n* **Vibe:** Professional, efficient, helpful",
  "type": "prompt",
  "description": "The primary orchestrator agent for this workspace.",
  "tools": [
    "workspace-manager",
    "agent-workflows"
  ],
  "topic": "General Expertise",
  "tone": "technical and precise",
  "style": "professional assistant",
  "goal": "Coordinate specialized agents and manage the workspace."
}
"""

IDENTITY_MD = """\
# IDENTITY.md - {display_name} Agent Identity

## [default]
 * **Name:** {display_name} Agent
 * **Role:** {description}
 * **Emoji:** 🤖

 ### System Prompt
 You are the {display_name} Agent.
 Use the `mcp-client` universal skill and check the reference documentation for
 `{package_name}.md` to discover the exact tags and tools available for your capabilities.

 ### Capabilities
 - **MCP Operations**: Leverage the `mcp-client` skill to interact with the target MCP server.
 - **Custom Agent**: Handle custom tasks or general tasks.
"""

GQL_PY = """\
#!/usr/bin/python
\"\"\"GraphQL API Wrapper for {display_name}.

Provides a GraphQL interface using the `gql` library that mirrors
REST API methods with GraphQL queries and mutations.

Requires: pip install {package_name}[gql]
\"\"\"

import logging
from typing import Any, Dict, Optional

from agent_utilities.core.decorators import require_auth
from agent_utilities.core.exceptions import (
    MissingParameterError,
    ParameterError,
)
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


class GraphQL:
    \"\"\"A class to interact with {display_name}'s GraphQL API.\"\"\"

    def __init__(
        self,
        url: str = None,
        token: str = None,
        proxies: Dict = None,
        verify: bool = True,
        debug: bool = False,
    ):
        if not url:
            raise MissingParameterError("URL is required")
        if not token:
            raise MissingParameterError("Token is required")

        self.url = f"{{url.rstrip('/')}}/api/graphql"
        self.token = token
        self.proxies = proxies
        self.verify = verify
        self.debug = debug

        logging.basicConfig(
            level=logging.DEBUG if debug else logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

        headers = {{"Authorization": f"Bearer {{token}}"}}
        self.transport = RequestsHTTPTransport(
            url=self.url,
            headers=headers,
            verify=verify,
            proxies=proxies,
        )
        self.client = Client(
            transport=self.transport, fetch_schema_from_transport=True
        )

    @require_auth
    def execute_gql(
        self,
        query_str: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        \"\"\"Execute a GraphQL query or mutation.\"\"\"
        try:
            query = gql(query_str)
            result = self.client.execute(
                query, variable_values=variables, operation_name=operation_name
            )
            if "errors" in result:
                raise ParameterError(f"GraphQL errors: {{result['errors']}}")
            return result
        except Exception as e:
            logging.error(f"GraphQL execution failed: {{str(e)}}")
            raise ParameterError(f"Query execution failed: {{str(e)}}")
"""

VALIDATE_AGENT_PY = """\
#!/usr/bin/env python3
\"\"\"Smoke-validate the A2A agent server entry point.\"\"\"

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from {pkg_dir}.agent_server import agent_server  # noqa: F401
except ImportError as e:
    print(f"Agent import failed: {{e}}")
    sys.exit(1)

print("Agent entry point import OK")
"""

# ── mkdocs + docs site (7 standard pages) ─────────────────────────────────────

MKDOCS_YML = """\
site_name: "{package_name}"
site_description: "{description}"
site_url: "https://knuckles-team.github.io/{package_name}/"
repo_name: "Knuckles-Team/{package_name}"
repo_url: "https://github.com/Knuckles-Team/{package_name}"
edit_uri: "edit/main/docs/"
copyright: "Copyright &copy; Knuckles-Team — MIT licensed"

theme:
  name: material
  icon:
    repo: fontawesome/brands/github
    logo: material/graph-outline
  favicon: https://raw.githubusercontent.com/squidfunk/mkdocs-material/master/material/templates/assets/images/favicon.png
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.sections
    - navigation.top
    - navigation.tracking
    - navigation.instant
    - navigation.instant.progress
    - navigation.footer
    - toc.follow
    - search.suggest
    - search.highlight
    - search.share
    - content.code.copy
    - content.code.annotate
    - content.tabs.link
    - content.tooltips
  palette:
    - media: "(prefers-color-scheme)"
      toggle:
        icon: material/brightness-auto
        name: Switch to light mode
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/weather-night
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/weather-sunny
        name: Switch to light mode

plugins:
  - search

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.emoji:
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
  - admonition
  - pymdownx.details
  - attr_list
  - md_in_html
  - tables
  - toc:
      permalink: true

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/Knuckles-Team/{package_name}
    - icon: fontawesome/brands/python
      link: https://pypi.org/project/{package_name}/

nav:
  - Home: index.md
  - Overview: overview.md
  - Installation: installation.md
  - Deployment: deployment.md
  - Usage (API / CLI / MCP): usage.md
  - Backing Platform ({display_name}): platform.md
  - Concepts: concepts.md
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

The connector remains inactive when credentials are absent: configure
`{service_url_env}` and `{auth_env}` to connect it to an instance.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Installation](installation.md)** — pip, source, extras, and the prebuilt Docker image.
- :material-server-network: **[Deployment](deployment.md)** — run the MCP and agent servers, Docker Compose, Caddy + Technitium.
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

- **Python 3.11 – 3.14**.
- A reachable target service instance and access token.

## From PyPI (recommended)

```bash
pip install {package_name}
```

### Optional extras

| Extra | Install | Pulls in |
|---|---|---|
| `mcp` | `pip install "{package_name}[mcp]"` | FastMCP MCP-server runtime (`agent-utilities[mcp]`) |
| `agent` | `pip install "{package_name}[agent]"` | Pydantic-AI agent + Logfire tracing |
| `all` | `pip install "{package_name}[all]"` | Everything above |

## From source

```bash
git clone https://github.com/Knuckles-Team/{package_name}.git
cd {package_name}
pip install -e ".[all]"
```

## Docker

```bash
docker pull knucklessg1/{package_name}:latest
```
"""

DOCS_DEPLOYMENT_MD = """\
# Deployment

This page covers running `{package_name}` as long-lived servers.

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
| 3 | Local container / uv | `stdio` or `streamable-http` | Docker / Podman / uv on this host | `command` or `url` |
| 4 | Remote URL | `streamable-http` | a remote host behind Caddy | `url` |

### 1. stdio (local subprocess)

```json
{{
  "mcpServers": {{
    "{mcp_cmd}": {{
      "command": "uvx",
      "args": ["--from", "{package_name}", "{mcp_cmd}"],
      "env": {{
        "{service_url_env}": "https://service.example.com",
        "{auth_env}": "your_token"
      }}
    }}
  }}
}}
```

### 2. Streamable-HTTP (local process)

```bash
uvx --from {package_name} {mcp_cmd} --transport streamable-http --host 0.0.0.0 --port 8000
curl -s http://localhost:8000/health        # {{"status":"OK"}}
```

Connect to the running process by URL:

```json
{{
  "mcpServers": {{
    "{mcp_cmd}": {{ "url": "http://localhost:8000/mcp" }}
  }}
}}
```

### 3. Local container / uv

Launch a container directly from `mcp_config.json` (swap `docker` for `podman` for a
daemonless runtime):

```json
{{
  "mcpServers": {{
    "{mcp_cmd}": {{
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "TRANSPORT=stdio",
        "-e", "{service_url_env}=https://service.example.com",
        "-e", "{auth_env}=your_token",
        "knucklessg1/{package_name}:latest"
      ]
    }}
  }}
}}
```

Or run a local streamable-http container and connect by URL:

```bash
docker compose -f docker/mcp.compose.yml up -d
```

```json
{{
  "mcpServers": {{
    "{mcp_cmd}": {{ "url": "http://localhost:8000/mcp" }}
  }}
}}
```

### 4. Remote URL (deployed behind Caddy)

When the server is deployed remotely and published through Caddy on the internal
`*.arpa` zone, connect with the `"url"` key — no local process or image required:

```json
{{
  "mcpServers": {{
    "{mcp_cmd}": {{ "url": "http://{mcp_cmd}.arpa/mcp" }}
  }}
}}
```

Caddy reverse-proxies `http://{mcp_cmd}.arpa` to the container's `:8000`
streamable-http listener.
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

api = get_client()        # reads {service_url_env} / {auth_env} from the environment / .env
status = api.get_system_status()
```

## As a CLI

```bash
export {service_url_env}="http://localhost:8080"
export {auth_env}="your_token"
{mcp_cmd} --transport stdio
```
"""

DOCS_PLATFORM_MD = """\
# Backing Platform — {display_name}

`{package_name}` is a **client** of a backing service instance. This page provides a
Docker recipe for deploying one locally to serve as the target of
`{service_url_env}`.

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

TESTS_AUTH = """\
from unittest.mock import patch

import pytest

import {pkg_dir}.auth as auth_module
from {pkg_dir}.auth import get_client


@pytest.mark.concept("{concept_prefix}-001")
def test_get_client_auth_error():
    \"\"\"Auth failure surfaces a clear error. CONCEPT:{concept_prefix}-001\"\"\"
    auth_module._client = None
    with patch("{pkg_dir}.auth.ApiClientSystem") as mock_client_cls:
        mock_client_cls.side_effect = Exception("Auth Failure")
        with pytest.raises(RuntimeError) as exc_info:
            get_client()
        assert "AUTHENTICATION ERROR" in str(exc_info.value)
    auth_module._client = None
"""

TESTS_API_WRAPPER = """\
from unittest.mock import MagicMock, patch

import pytest

from {pkg_dir}.api import ApiClientBase


@pytest.mark.concept("{concept_prefix}-001")
def test_request_returns_json():
    \"\"\"API client returns parsed JSON. CONCEPT:{concept_prefix}-001\"\"\"
    client = ApiClientBase(base_url="http://localhost", token="t")
    response = MagicMock()
    response.json.return_value = {{"ok": True}}
    with patch.object(client.session, "request", return_value=response):
        assert client.request("GET", "/health") == {{"ok": True}}
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
    assert "CONCEPT:{concept_prefix}-" in CONCEPTS_DOC.read_text(encoding="utf-8")
"""


# ── Main Scaffolding Logic ───────────────────────────────────────────────────


def scaffold(
    package_name: str,
    output_dir: str = ".",
    pkg_types: str = "api_client,mcp,agent",
    display_name: str = "",
    description: str = "",
    author: str = "Audel Rouhi",
    email: str = "knucklessg1@gmail.com",
    service_url_env: str = "",
    auth_env: str = "",
    concept_prefix: str = "",
    doc_urls: str = "",
    in_place: bool = False,
):
    """Scaffold a complete agent-package project (gitlab-api golden parity)."""
    types = [t.strip() for t in pkg_types.split(",")]
    pkg_dir = to_pkg_dir(package_name)
    if not display_name:
        display_name = to_display(package_name)
    if not description:
        description = f"{display_name} API + MCP Server + A2A Server"
    upper_name = to_upper_env(package_name)
    if not service_url_env:
        service_url_env = f"{upper_name}_URL"
    if not auth_env:
        auth_env = f"{upper_name}_TOKEN"
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

    ssl_verify_env = f"{upper_name}_SSL_VERIFY"
    year = datetime.datetime.now().year
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    has_graphql = "graphql" in types
    gql_core_dep = ' "gql[requests]>=4.0.0",' if has_graphql else ""
    gql_extra = 'gql = [ "gql[requests]>=4.0.0",]\n' if has_graphql else ""
    all_extras = "mcp,agent,gql,logfire" if has_graphql else "mcp,agent,logfire"
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
        "author": author,
        "email": email,
        "service_url_env": service_url_env,
        "auth_env": auth_env,
        "ssl_verify_env": ssl_verify_env,
        "concept_prefix": concept_prefix,
        "mcp_cmd": mcp_cmd,
        "agent_cmd": agent_cmd,
        "short_name": short_name,
        "agent_port": "9000",
        "gql_core_dep": gql_core_dep,
        "gql_extra": gql_extra,
        "all_extras": all_extras,
        "gql_optional_module": gql_optional_module,
        "gql_all_extend": gql_all_extend,
        "year": year,
        "date": date,
        "upper_name": upper_name,
    }

    root = Path(output_dir) if in_place else Path(output_dir) / package_name
    pkg = root / pkg_dir

    # files: path -> (template, needs_format)
    files = {
        # Root configs
        root / "pyproject.toml": (PYPROJECT_TOML, True),
        root / ".bumpversion.cfg": (BUMPVERSION_CFG, True),
        root / ".pre-commit-config.yaml": (PRECOMMIT_CONFIG, False),
        root / ".dockerignore": (DOCKERIGNORE, True),
        root / ".env.example": (ENV_EXAMPLE, True),
        root / ".env": (ENV_EXAMPLE, True),
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
        root / ".github/workflows/docs.yml": (DOCS_YML, False),
        root / ".github/workflows/pages.yml": (PAGES_YML, False),
        # Docs site (7 standard pages)
        root / "mkdocs.yml": (MKDOCS_YML, True),
        root / "docs/index.md": (DOCS_INDEX_MD, True),
        root / "docs/overview.md": (DOCS_OVERVIEW_MD, True),
        root / "docs/installation.md": (DOCS_INSTALLATION_MD, True),
        root / "docs/deployment.md": (DOCS_DEPLOYMENT_MD, True),
        root / "docs/usage.md": (DOCS_USAGE_MD, True),
        root / "docs/platform.md": (DOCS_PLATFORM_MD, True),
        root / "docs/concepts.md": (DOCS_CONCEPTS_MD, True),
        # Repo scripts
        root / "scripts/validate_agent.py": (VALIDATE_AGENT_PY, True),
    }

    # Package files
    files[pkg / "__init__.py"] = (INIT_PY, True)
    files[pkg / "auth.py"] = (AUTH_PY, True)
    files[pkg / "api_client.py"] = (API_CLIENT_FACADE, False)
    files[pkg / f"{to_pkg_dir(short_name)}_input_models.py"] = (INPUT_MODELS_PY, True)
    files[pkg / f"{to_pkg_dir(short_name)}_response_models.py"] = (
        RESPONSE_MODELS_PY,
        True,
    )
    files[pkg / "mcp_config.json"] = (PKG_MCP_CONFIG_JSON, False)
    files[pkg / "main_agent.json"] = (MAIN_AGENT_JSON, False)

    # API modular directory scaffolding
    files[pkg / "api" / "__init__.py"] = (API_INIT_PY, False)
    files[pkg / "api" / "api_client_base.py"] = (API_CLIENT_BASE, True)
    files[pkg / "api" / "api_client_system.py"] = (API_CLIENT_SYSTEM, True)

    # MCP modular directory scaffolding
    files[pkg / "mcp" / "__init__.py"] = (MCP_INIT_PY, False)
    files[pkg / "mcp" / "mcp_system.py"] = (MCP_SYSTEM_PY, True)

    if "mcp" in types:
        files[pkg / "mcp_server.py"] = (MCP_SERVER_PY, True)

    if "agent" in types:
        files[pkg / "agent_server.py"] = (AGENT_SERVER_PY, True)
        files[pkg / "__main__.py"] = (MAIN_PY, True)
        files[pkg / "agent_data" / "IDENTITY.md"] = (IDENTITY_MD, True)

    if has_graphql:
        files[pkg / f"{gql_module_name}.py"] = (GQL_PY, True)

    # Flat tests directory
    files[root / "tests" / "__init__.py"] = ("", False)
    files[root / "tests" / "conftest.py"] = (TESTS_CONFTEST, True)
    files[root / "tests" / "test_auth.py"] = (TESTS_AUTH, True)
    files[root / "tests" / "test_api_wrapper.py"] = (TESTS_API_WRAPPER, True)
    files[root / "tests" / f"test_{to_pkg_dir(short_name)}_mcp_validation.py"] = (
        TESTS_MCP_VALIDATION,
        True,
    )
    files[root / "tests" / "test_init_dynamics.py"] = (TESTS_INIT_DYNAMICS, True)
    files[root / "tests" / "test_startup.py"] = (TESTS_STARTUP, True)
    files[root / "tests" / "test_concept_parity.py"] = (TESTS_CONCEPT_PARITY, True)

    # ── Write all files ──────────────────────────────────────────────────
    for path, (template, needs_format) in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        content = template.format(**ctx) if needs_format else template
        path.write_text(content, encoding="utf-8")
        print(f"  ✅ {path.relative_to(root.parent)}")

    # Bundled golden validation scripts (verbatim from gitlab-api)
    for script_name in (
        "security_sanitizer.py",
        "verify_api_integration.py",
        "validate_a2a_agent.py",
    ):
        src = TEMPLATES_DIR / script_name
        dst = root / "scripts" / script_name
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            print(f"  ✅ {dst.relative_to(root.parent)} (bundled golden script)")
        else:
            print(
                f"  ⚠️  {script_name} template missing — copy it from "
                "agents/gitlab-api/scripts/ manually"
            )

    # requirements.txt mirrors [project].dependencies
    import tomllib

    pyproject_content = (root / "pyproject.toml").read_text(encoding="utf-8")
    parsed_toml = tomllib.loads(pyproject_content)
    deps = parsed_toml.get("project", {}).get("dependencies", [])

    req_path = root / "requirements.txt"
    req_path.write_text("\n".join(deps) + "\n", encoding="utf-8")
    print(f"  ✅ {req_path.relative_to(root.parent)}")

    print(f"\n🎉 Scaffolded '{package_name}' at {root.resolve()}")
    print(f"   Package dir: {pkg_dir}/")
    print(f"   Console scripts: {mcp_cmd}, {agent_cmd}")
    print(f"   Concept prefix: CONCEPT:{concept_prefix}-*")
    print(f"   Types: {', '.join(types)}")
    print("   → Run `uv lock` to generate uv.lock (required by the pre-commit gate).")
    if doc_urls:
        print(f"   Doc URLs saved: {doc_urls}")
        print("   → Run skill-graph-builder to generate docs skill.")


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scaffold a complete agent-package project following the gitlab-api golden standard."
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
        default="api_client,mcp,agent",
        dest="pkg_types",
        type=str,
        help="Comma-separated types: api_client, mcp, agent, graphql (default: api_client,mcp,agent)",
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
        "--author",
        default="Audel Rouhi",
        help="Author name (default: Audel Rouhi)",
    )
    parser.add_argument(
        "--email",
        default="knucklessg1@gmail.com",
        help="Author email (default: knucklessg1@gmail.com)",
    )
    parser.add_argument(
        "--service-url-env",
        default="",
        help="Environment variable name for service URL (default: {UPPER_NAME}_URL)",
    )
    parser.add_argument(
        "--auth-env",
        default="",
        help="Environment variable name for auth token (default: {UPPER_NAME}_TOKEN)",
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

    args = parser.parse_args()
    scaffold(
        package_name=args.package_name,
        output_dir=args.output_dir,
        pkg_types=args.pkg_types,
        display_name=args.display_name,
        description=args.description,
        author=args.author,
        email=args.email,
        service_url_env=args.service_url_env,
        auth_env=args.auth_env,
        concept_prefix=args.concept_prefix,
        doc_urls=args.doc_urls,
        in_place=args.in_place,
    )
