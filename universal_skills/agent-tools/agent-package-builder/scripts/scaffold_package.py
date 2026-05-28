#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Package Builder — Scaffolds a complete agent-package project.

Generates the full project structure following the jellyfin-mcp gold standard,
including modular split folders for api/ and mcp/, modern Material theme mkdocs,
Keep a Changelog CHANGELOG.md, and unified pytest layout.
"""

import argparse
import datetime
from pathlib import Path

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


# ── Templates ────────────────────────────────────────────────────────────────

PYPROJECT_TOML = """\
[build-system]
requires = ["setuptools>=80.9.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{package_name}"
version = "0.1.0"
description = "{description}"
readme = "README.md"
authors = [{{ name = "{author}", email = "{email}" }}]
license = {{ text = "MIT" }}
classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Environment :: Console",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3"]
requires-python = ">=3.10"
dependencies = [
    "agent-utilities[mcp]>=0.2.12"]

[project.optional-dependencies]
agent = [
    "agent-utilities[agent,logfire]>=0.2.12"]
{gql_dep}
all = [
    "{all_dep_line}"]

[project.scripts]
{mcp_cmd} = "{pkg_dir}.mcp_server:mcp_server"
{agent_cmd} = "{pkg_dir}.agent_server:agent_server"

[tool.setuptools.packages.find]
where = ["."]

[tool.setuptools]
include-package-data = true

[tool.setuptools.package-data]
{pkg_dir} = [ "mcp_config.json", "agent/**", "skills/**"]
"""

BUMPVERSION_CFG = """\
[bumpversion]
current_version = 0.1.0
commit = True
tag = True

[bumpversion:file:pyproject.toml]
search = version = "{{current_version}}"
replace = version = "{{new_version}}"

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

PRECOMMIT_CONFIG = """\
default_language_version:
  python: python3
exclude: 'dotnet'
ci:
  autofix_prs: true
  autoupdate_commit_msg: '[pre-commit.ci] pre-commit suggestions'
  autoupdate_schedule: 'monthly'

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
    - id: check-added-large-files
      exclude: '{pkg_dir}/skills/.*-docs/'
    - id: check-ast
    - id: check-yaml
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
    rev: v0.15.4
    hooks:
      - id: ruff
        exclude: ^(tests/|test/|scripts/|script/)
        types_or: [ python, pyi, jupyter ]
        args: ["--fix", "--ignore=E402"]
  - repo: https://github.com/codespell-project/codespell
    rev: v2.4.1
    hooks:
      - id: codespell
        args: ["-L", "nam,tread,ot,"]
        exclude: |
            (?x)^(
              \\./test/.*|
              \\./tests/.*|
              {pkg_dir}/skills/.*-docs/.*
            )$
  - repo: https://github.com/nbQA-dev/nbQA
    rev: 1.9.1
    hooks:
      - id: nbqa-ruff
        exclude: ^(tests/|test/|scripts/|script/)
"""

DOCKERFILE = """\
FROM python:3-slim

ARG HOST=0.0.0.0
ARG PORT=8000
ARG TRANSPORT="http"
ARG AUTH_TYPE="none"
ARG TOKEN_JWKS_URI=""
ARG TOKEN_ISSUER=""
ARG TOKEN_AUDIENCE=""
ARG OAUTH_UPSTREAM_AUTH_ENDPOINT=""
ARG OAUTH_UPSTREAM_TOKEN_ENDPOINT=""
ARG OAUTH_UPSTREAM_CLIENT_ID=""
ARG OAUTH_UPSTREAM_CLIENT_SECRET=""
ARG OAUTH_BASE_URL=""
ARG OIDC_CONFIG_URL=""
ARG OIDC_CLIENT_ID=""
ARG OIDC_CLIENT_SECRET=""
ARG OIDC_BASE_URL=""
ARG REMOTE_AUTH_SERVERS=""
ARG REMOTE_BASE_URL=""
ARG ALLOWED_CLIENT_REDIRECT_URIS=""
ARG EUNOMIA_TYPE="none"
ARG EUNOMIA_POLICY_FILE="mcp_policies.json"
ARG EUNOMIA_REMOTE_URL=""

ENV HOST=${{HOST}} \\
    PORT=${{PORT}} \\
    TRANSPORT=${{TRANSPORT}} \\
    AUTH_TYPE=${{AUTH_TYPE}} \\
    TOKEN_JWKS_URI=${{TOKEN_JWKS_URI}} \\
    TOKEN_ISSUER=${{TOKEN_ISSUER}} \\
    TOKEN_AUDIENCE=${{TOKEN_AUDIENCE}} \\
    OAUTH_UPSTREAM_AUTH_ENDPOINT=${{OAUTH_UPSTREAM_AUTH_ENDPOINT}} \\
    OAUTH_UPSTREAM_TOKEN_ENDPOINT=${{OAUTH_UPSTREAM_TOKEN_ENDPOINT}} \\
    OAUTH_UPSTREAM_CLIENT_ID=${{OAUTH_UPSTREAM_CLIENT_ID}} \\
    OAUTH_UPSTREAM_CLIENT_SECRET=${{OAUTH_UPSTREAM_CLIENT_SECRET}} \\
    OAUTH_BASE_URL=${{OAUTH_BASE_URL}} \\
    OIDC_CONFIG_URL=${{OIDC_CONFIG_URL}} \\
    OIDC_CLIENT_ID=${{OIDC_CLIENT_ID}} \\
    OIDC_CLIENT_SECRET=${{OIDC_CLIENT_SECRET}} \\
    OIDC_BASE_URL=${{OIDC_BASE_URL}} \\
    REMOTE_AUTH_SERVERS=${{REMOTE_AUTH_SERVERS}} \\
    REMOTE_BASE_URL=${{REMOTE_BASE_URL}} \\
    ALLOWED_CLIENT_REDIRECT_URIS=${{ALLOWED_CLIENT_REDIRECT_URIS}} \\
    EUNOMIA_TYPE=${{EUNOMIA_TYPE}} \\
    EUNOMIA_POLICY_FILE=${{EUNOMIA_POLICY_FILE}} \\
    EUNOMIA_REMOTE_URL=${{EUNOMIA_REMOTE_URL}} \\
    PYTHONUNBUFFERED=1 \\
    PATH="/root/.local/bin:/usr/local/bin:${{PATH}}" \\
    UV_HTTP_TIMEOUT=3600 \\
    UV_SYSTEM_PYTHON=1 \\
    UV_COMPILE_BYTECODE=1

RUN apt-get update \\
    && apt-get install -y default-jre ripgrep tree fd-find curl nano \\
    && curl -LsSf https://astral.sh/uv/install.sh | sh \\
    && curl -sS https://starship.rs/install.sh | sh -s -- --yes \\
    && mkdir -p /root/.config \\
    && echo 'eval "$(starship init bash)"' >> /root/.bashrc \\
    && uv pip install --system --upgrade --verbose --no-cache --break-system-packages --prerelease=allow {package_name}[all]>=0.1.0

COPY starship.toml /root/.config/starship.toml

CMD ["{mcp_cmd}"]
"""

DEBUG_DOCKERFILE = """\
FROM python:3-slim

ARG HOST=0.0.0.0
ARG PORT=8000
ARG TRANSPORT="http"
ARG AUTH_TYPE="none"
ARG TOKEN_JWKS_URI=""
ARG TOKEN_ISSUER=""
ARG TOKEN_AUDIENCE=""
ARG OAUTH_UPSTREAM_AUTH_ENDPOINT=""
ARG OAUTH_UPSTREAM_TOKEN_ENDPOINT=""
ARG OAUTH_UPSTREAM_CLIENT_ID=""
ARG OAUTH_UPSTREAM_CLIENT_SECRET=""
ARG OAUTH_BASE_URL=""
ARG OIDC_CONFIG_URL=""
ARG OIDC_CLIENT_ID=""
ARG OIDC_CLIENT_SECRET=""
ARG OIDC_BASE_URL=""
ARG REMOTE_AUTH_SERVERS=""
ARG REMOTE_BASE_URL=""
ARG ALLOWED_CLIENT_REDIRECT_URIS=""
ARG EUNOMIA_TYPE="none"
ARG EUNOMIA_POLICY_FILE="mcp_policies.json"
ARG EUNOMIA_REMOTE_URL=""

ENV HOST=${{HOST}} \\
    PORT=${{PORT}} \\
    TRANSPORT=${{TRANSPORT}} \\
    AUTH_TYPE=${{AUTH_TYPE}} \\
    TOKEN_JWKS_URI=${{TOKEN_JWKS_URI}} \\
    TOKEN_ISSUER=${{TOKEN_ISSUER}} \\
    TOKEN_AUDIENCE=${{TOKEN_AUDIENCE}} \\
    OAUTH_UPSTREAM_AUTH_ENDPOINT=${{OAUTH_UPSTREAM_AUTH_ENDPOINT}} \\
    OAUTH_UPSTREAM_TOKEN_ENDPOINT=${{OAUTH_UPSTREAM_TOKEN_ENDPOINT}} \\
    OAUTH_UPSTREAM_CLIENT_ID=${{OAUTH_UPSTREAM_CLIENT_ID}} \\
    OAUTH_UPSTREAM_CLIENT_SECRET=${{OAUTH_UPSTREAM_CLIENT_SECRET}} \\
    OAUTH_BASE_URL=${{OAUTH_BASE_URL}} \\
    OIDC_CONFIG_URL=${{OIDC_CONFIG_URL}} \\
    OIDC_CLIENT_ID=${{OIDC_CLIENT_ID}} \\
    OIDC_CLIENT_SECRET=${{OIDC_CLIENT_SECRET}} \\
    OIDC_BASE_URL=${{OIDC_BASE_URL}} \\
    REMOTE_AUTH_SERVERS=${{REMOTE_AUTH_SERVERS}} \\
    REMOTE_BASE_URL=${{REMOTE_BASE_URL}} \\
    ALLOWED_CLIENT_REDIRECT_URIS=${{ALLOWED_CLIENT_REDIRECT_URIS}} \\
    EUNOMIA_TYPE=${{EUNOMIA_TYPE}} \\
    EUNOMIA_POLICY_FILE=${{EUNOMIA_POLICY_FILE}} \\
    EUNOMIA_REMOTE_URL=${{EUNOMIA_REMOTE_URL}} \\
    PYTHONUNBUFFERED=1 \\
    PATH="/root/.local/bin:/usr/local/bin:${{PATH}}" \\
    UV_HTTP_TIMEOUT=3600 \\
    UV_SYSTEM_PYTHON=1 \\
    UV_COMPILE_BYTECODE=1

WORKDIR /app
COPY . /app
RUN apt-get update \\
    && apt-get install -y default-jre ripgrep tree fd-find curl nano \\
    && curl -LsSf https://astral.sh/uv/install.sh | sh \\
    && curl -sS https://starship.rs/install.sh | sh -s -- --yes \\
    && mkdir -p /root/.config \\
    && echo 'eval "$(starship init bash)"' >> /root/.bashrc \\
    && uv pip install --system --upgrade --verbose --no-cache --break-system-packages --prerelease=allow .[all]

COPY starship.toml /root/.config/starship.toml

CMD ["{mcp_cmd}"]
"""

COMPOSE_YML = """\
---
services:
  {agent_service_name}:
    # image: docker.io/knucklessg1/{package_name}:latest
    build:
      context: .. # Debug
      dockerfile: docker/debug.Dockerfile
    container_name: {agent_service_name}
    hostname: {agent_service_name}
    command: [ "{agent_cmd}" ]
    extra_hosts:
      - "host.docker.internal:host-gateway"
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    restart: always
    env_file:
      - ../.env
    environment:
      - "HOST=0.0.0.0"
      - "PORT=9001"
      - "TRANSPORT=stdio"
      - "{service_url_env}=${{{service_url_env}}}"
      - "{auth_env}=${{{auth_env}}}"
      - "PROVIDER=openai"
      - "LLM_BASE_URL=${{LLM_BASE_URL:-http://host.docker.internal:1234/v1}}"
      - "LLM_API_KEY=${{LLM_API_KEY:-llama}}"
      - "MODEL_ID=${{MODEL_ID:-qwen/qwen3.5-9b}}"
      - "DEBUG=False"
      - "ENABLE_WEB_UI=True"
      - "ENABLE_OTEL=True"
    ports:
      - "9001:9001"
    healthcheck:
      test: [ "CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:9001/health')" ]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
"""

MCP_COMPOSE_YML = """\
---
services:
  {mcp_cmd}:
    build:
      context: .. # Production
      dockerfile: docker/debug.Dockerfile # Using debug for local dev usually
    container_name: {mcp_cmd}
    hostname: {mcp_cmd}
    command: [ "{mcp_cmd}" ]
    extra_hosts:
      - "host.docker.internal:host-gateway"
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    restart: always
    volumes:
      - ../mcp:/app
    env_file:
      - ../.env
    environment:
      - "PYTHONUNBUFFERED=1"
      - "HOST=0.0.0.0"
      - "PORT=8004"
      - "TRANSPORT=streamable-http"
    ports:
      - "8004:8004"
    healthcheck:
      test: [ "CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8004/health')" ]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  {agent_service_name}:
    build:
      context: .. # Production
      dockerfile: docker/debug.Dockerfile
    container_name: {agent_service_name}
    hostname: {agent_service_name}
    command: [ "{agent_cmd}" ]
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - {mcp_cmd}
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    restart: always
    env_file:
      - ../.env
    environment:
      - "PYTHONUNBUFFERED=1"
      - "HOST=0.0.0.0"
      - "PORT=9004"
      - "MCP_URL=http://{mcp_cmd}:8004/mcp"
      - "PROVIDER=openai"
      - "LLM_BASE_URL=${{LLM_BASE_URL:-http://host.docker.internal:1234/v1}}"
      - "LLM_API_KEY=${{LLM_API_KEY:-llama}}"
      - "MODEL_ID=${{MODEL_ID:-qwen/qwen3.5-9b}}"
      - "DEBUG=False"
      - "ENABLE_WEB_UI=True"
      - "ENABLE_OTEL=True"
    ports:
      - "9004:9004"
    healthcheck:
      test: [ "CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:9004/health')" ]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
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
*.egg-info*
models/
.github/
build/
.bumpversion.cfg
.pre-commit-config.yaml
pytest.ini
./tests/

docker/Dockerfile
docker/debug.Dockerfile
docker/compose.yml
docker/mcp.compose.yml
"""

ENV_TEMPLATE = """\
LLM_BASE_URL=http://vllm.arpa/v1
LLM_API_KEY=llama
ENABLE_OTEL=True
OTEL_EXPORTER_OTLP_ENDPOINT=http://langfuse.arpa/api/public/otel
OTEL_EXPORTER_OTLP_PUBLIC_KEY=""
OTEL_EXPORTER_OTLP_SECRET_KEY=""
OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
{service_url_env}=http://localhost:8080
{auth_env}=your_token_here
"""

REQUIREMENTS_TXT = """\
requests>=2.8.1
urllib3>=2.2.2
fastmcp>=2.13.0.2
uvicorn>=0.29.0
fastapi>=0.110.0
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
recursive-include {pkg_dir} *.md *.json *.yaml *.yml *.py
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

# PyInstaller
*.manifest
*.spec

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

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
# .python-version

# pipenv
#Pipfile.lock

# UV
#uv.lock

# poetry
#poetry.lock
#poetry.toml

# pdm
#pdm.lock
#pdm.toml
.pdm-python
.pdm-build/

# pixi
#pixi.lock
.pixi

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.envrc
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# Abstra
.abstra/

# Ruff stuff:
.ruff_cache/

# PyPI configuration file
.pypirc

# Cursor
.cursorignore
.cursorindexingignore

# Marimo
marimo/_static/
marimo/_lsp/
__marimo__/
"""

GITATTRIBUTES = """\
# Auto detect
*                 text=auto

# Source code
*.bash            text eol=lf
*.bat             text eol=crlf
*.cmd             text eol=crlf
*.coffee          text
*.css             text diff=css
*.htm             text diff=html
*.html            text diff=html
*.inc             text
*.ini             text
*.js              text
*.json            text
*.jsx             text
*.less            text
*.ls              text
*.map             text -diff
*.od              text
*.onlydata        text
*.php             text diff=php
*.pl              text
*.ps1             text eol=crlf
*.py              text diff=python
*.rb              text diff=ruby
*.sass            text
*.scm             text
*.scss            text diff=css
*.sh              text eol=lf
.husky/*          text eol=lf
*.sql             text
*.styl            text
*.tag             text
*.ts              text
*.tsx             text
*.xml             text
*.xhtml           text diff=html

# Docker
Dockerfile        text

# Documentation
*.ipynb           text
*.markdown        text diff=markdown eol=lf
*.md              text diff=markdown eol=lf
*.mdwn            text diff=markdown eol=lf
*.mdown           text diff=markdown eol=lf
*.mkd             text diff=markdown eol=lf
*.mkdn            text diff=markdown eol=lf
*.mdtxt           text eol=lf
*.mdtext          text eol=lf
*.txt             text
AUTHORS           text
CHANGELOG         text
CHANGES           text
CONTRIBUTING      text
COPYING           text
copyright         text
*COPYRIGHT*       text
INSTALL           text
license           text
LICENSE           text
NEWS              text
readme            text
*README*          text
TODO              text
"""

README_MD = """\
# {display_name} - A2A | AG-UI | MCP

*Version: 0.1.0*

## Overview

**{display_name} MCP Server + A2A Agent**

{description}

This repository is actively maintained - Contributions are welcome!

## MCP

### Using as an MCP Server

The MCP Server can be run in two modes: `stdio` (for local testing) or `http` (for networked access).

#### Environment Variables

*   `{service_url_env}`: The URL of the target service.
*   `{auth_env}`: The API token or access token.

#### Run in stdio mode (default):
```bash
export {service_url_env}="http://localhost:8080"
export {auth_env}="your_token"
{mcp_cmd} --transport "stdio"
```

## Install Python Package

```bash
python -m pip install {package_name}
```
"""

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

_MCP_AVAILABLE = OPTIONAL_MODULES.get("{pkg_dir}.mcp_server") in [
    m.__name__ for m in globals().values() if hasattr(m, "__name__")
]
_AGENT_AVAILABLE = "{pkg_dir}.agent_server" in globals()

__all__.extend(["_MCP_AVAILABLE", "_AGENT_AVAILABLE"{gql_all_extend}])
"""

AUTH_PY = """\
#!/usr/bin/python
# coding: utf-8

import os
from agent_utilities.core.exceptions import AuthError, UnauthorizedError
from .api import ApiClientSystem

_client = None


def get_client() -> ApiClientSystem:
    \"\"\"Get or create a singleton API client instance.\"\"\"
    global _client
    if _client is None:
        base_url = os.getenv("{service_url_env}", "http://localhost:8080")
        token = os.getenv("{auth_env}", "")
        verify = os.getenv("{verify_env}", "True").lower() in ("true", "1", "yes")

        try:
            _client = ApiClientSystem(
                base_url=base_url,
                token=token,
                verify=verify,
            )
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
# coding: utf-8

import os
import sys
import logging
from typing import Any
from dotenv import load_dotenv, find_dotenv
from fastmcp import FastMCP
from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import create_mcp_server
from agent_utilities.utilities import get_logger
from .mcp import register_system_tools

__version__ = "0.1.0"

logger = get_logger(name="MCP_Server")
logger.setLevel(logging.INFO)


def get_mcp_instance() -> tuple[Any, Any, Any]:
    \"\"\"Initialize and return the {display_name} MCP instance, args, and middlewares.\"\"\"
    load_dotenv(find_dotenv())

    args, mcp, middlewares = create_mcp_server(
        name="{display_name} MCP",
        version=__version__,
        instructions="{display_name} MCP Server — Condensed Action-Routed Tools.",
    )

    DEFAULT_SYSTEMTOOL = to_boolean(os.getenv("SYSTEMTOOL", "True"))
    if DEFAULT_SYSTEMTOOL:
        register_system_tools(mcp)

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

# ── Split directories layout ───────────────────────────────────────────

API_CLIENT_BASE = """\
import os
import requests
from typing import Dict, Any

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
from .api_client_base import ApiClientBase
from typing import Dict, Any

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

MCP_SYSTEM_PY = """\
from fastmcp import FastMCP, Context
from fastmcp.dependencies import Depends
from pydantic import Field
from ..auth import get_client

def register_system_tools(mcp: FastMCP):
    \"\"\"Register system tag dynamic tools.\"\"\"
    @mcp.tool(tags={{"system"}})
    async def system_operations(
        action: str = Field(
            description="Action to perform. Must be 'status' or 'info'."
        ),
        params_json: str = Field(
            default="{{}}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        \"\"\"Manage system tag operations.\"\"\"
        if ctx:
            ctx.info("Executing system tool...")
        import json
        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {{"error": f"Invalid params_json: {{e}}"}}

        if action == "status":
            try:
                return client.get_system_status()
            except Exception as e:
                return {{"error": str(e)}}
        else:
            return {{"info": "System operations dynamic placeholder."}}
"""

MCP_INIT_PY = """\
from .mcp_system import register_system_tools

__all__ = ["register_system_tools"]
"""

# ── Docs ───────────────────────────────────────────────────────────────

MKDOCS_YML = """\
site_name: "{package_name}"
repo_name: "Knuckles-Team/{package_name}"
repo_url: "https://github.com/Knuckles-Team/{package_name}"
theme:
  name: material
  features:
    - navigation.sections
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.code.annotate
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/weather-night
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/weather-sunny
        name: Switch to light mode
  icon:
    repo: fontawesome/brands/github
plugins:
  - search
markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - admonition
  - pymdownx.details
  - attr_list
  - tables
  - toc:
      permalink: true
nav:
  - Home: index.md
  - Overview: overview.md
"""

DOCS_INDEX_MD = """\
# {display_name} Documentation

Welcome to the documentation for **{display_name}**!

This project provides a unified Model Context Protocol (MCP) server and A2A Agent designed to integrate with standard tools and clients seamlessly.

## Getting Started

Refer to the [Overview](overview.md) or the [README](../README.md) for quick start instructions.
"""

DOCS_OVERVIEW_MD = """\
# {display_name} Overview

This agent package provides premium tools and workflows for interacting with the target service.

## Key Features
- **Modular Design**: Broken up into `api/` and `mcp/` directories for cleaner organization.
- **Dynamic Tool Registration**: Exposes action-routed dynamic tool tags strictly complying with lowercase tags constraint.
- **Test Automation**: Shipped with flat-file `tests/` directory covering auth error cases and API verification.
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
- Modular subfolders for API wrappers (`api/`) and MCP servers (`mcp/`).
- Modernized material theme mkdocs setup.
- Flat `tests/` structure for comprehensive endpoint verification.
"""

# ── Tests ──────────────────────────────────────────────────────────────

TESTS_CONFTEST = """\
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_api_client():
    client = MagicMock()
    client.get_system_status.return_value = {{"status": "OK"}}
    return client
"""

TESTS_API_AUTH = """\
import pytest
from unittest.mock import patch
from {pkg_dir}.auth import get_client

def test_get_client_auth_error():
    # Test instantiating the api client base setup
    with patch("{pkg_dir}.auth.ApiClientSystem") as mock_client_cls:
        mock_client_cls.side_effect = Exception("Auth Failure")
        with pytest.raises(RuntimeError) as exc_info:
            get_client()
        assert "AUTHENTICATION ERROR" in str(exc_info.value)
"""

TESTS_MCP_SERVER = """\
import pytest
from {pkg_dir}.mcp_server import get_mcp_instance

def test_mcp_instance_registration():
    mcp, args, middlewares = get_mcp_instance()
    assert mcp is not None
    # Verify that the system tool was registered correctly
    tools = [t.name for t in mcp.tools]
    assert any("system_operations" in t for t in tools)
"""


# ── Rest of agent templates ───────────────────────────────────────────

AGENT_PY = """\
#!/usr/bin/python
# coding: utf-8
import os
import sys
import logging
import warnings
from pathlib import Path

from agent_utilities import (
    build_system_prompt_from_workspace,
    create_agent_parser,
    create_agent_server,
    initialize_workspace,
    load_identity,
    get_workspace_path,
)

__version__ = "0.1.0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load identity and system prompt from workspace
initialize_workspace()
meta = load_identity()
DEFAULT_AGENT_NAME = os.getenv("DEFAULT_AGENT_NAME", meta.get("name", "{display_name}"))
DEFAULT_AGENT_DESCRIPTION = os.getenv(
    "AGENT_DESCRIPTION",
    meta.get("description", "{description}"),
)
DEFAULT_AGENT_SYSTEM_PROMPT = os.getenv(
    "AGENT_SYSTEM_PROMPT",
    meta.get("content") or build_system_prompt_from_workspace(),
)


def agent_server():
    warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="fastmcp")

    print(f"{{DEFAULT_AGENT_NAME}} v{{__version__}}", file=sys.stderr)
    parser = create_agent_parser()
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    # Start server using the auto-discovery pattern (from mcp_config.json)
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
# coding: utf-8
from {pkg_dir}.agent_server import agent_server

if __name__ == "__main__":
    agent_server()
"""

IDENTITY_MD = """\
# IDENTITY.md - {display_name} Agent Identity

## [default]
 * **Name:** {display_name} Agent
 * **Role:** {description}
 * **Emoji:** 🤖

 ### System Prompt
 You are the {display_name} Agent.
 You must always first run `list_skills` to show all skills.
 Then, use the `mcp-client` universal skill and check the reference documentation for `{package_name}.md` to discover the exact tags and tools available for your capabilities.

 ### Capabilities
 - **MCP Operations**: Leverage the `mcp-client` skill to interact with the target MCP server. Refer to `{package_name}.md` for specific tool capabilities.
 - **Custom Agent**: Handle custom tasks or general tasks.
"""

CRON_MD = """\
# CRON.md - Persistent Scheduled Tasks
Last updated: {date}

## Active Tasks

| ID          | Name              | Interval (min) | Prompt                              | Last run          | Next approx |
|-------------|-------------------|----------------|-------------------------------------|-------------------|-------------|
| heartbeat   | Heartbeat         | 30             | @HEARTBEAT.md                       | —                 | —           |
| log-cleanup | Log Cleanup       | 720            | __internal:cleanup_cron_log         | —                 | —           |

*Edit this table to add/remove tasks. The agent reloads it periodically.*
*Use `@filename.md` in the Prompt column to load a multi-line prompt from a workspace file.*
"""

HEARTBEAT_MD = """\
# Heartbeat — Periodic Self-Check

You are running a scheduled heartbeat. Perform these checks and report results concisely.

## Checks

1. **Tool Availability** — Call `list_tools` or equivalent to verify your MCP tools are reachable. Report any connection failures.
2. **Memory Review** — Query the **Knowledge Graph** for any pending follow-up tasks, architectural decisions, or action items.
3. **Cron Log** — Read `CRON_LOG.md` and check for recent errors (❌). Summarize any failures from the last 24 hours.
4. **Peer Agents** — Read `AGENTS.md` and note if any registered peers need attention.
5. **Domain-Specific Checks**:
   - **Service Health**: Check service health status and scan recent logs for critical errors using available tools.
6. **Self-Diagnostics** — Report your current model, available tool count, and any anomalies.

## Response Format

If everything is healthy:
```
HEARTBEAT_OK — All systems nominal. [tool_count] tools available. No pending actions.
```

If issues found:
```
HEARTBEAT_ALERT — [summary of issues found]
- Issue 1: ...
- Issue 2: ...
- Action needed: ...
```
"""
CRON_LOG_MD = """# CRON_LOG.md - Scheduled Task History
Last updated: {date}

| Timestamp | Task ID | Status | Message |
|-----------|---------|--------|---------|
"""

MCP_CONFIG_MD = """{{
  "mcpServers": {{
    "{mcp_short_name}": {{
      "command": "{mcp_cmd}",
      "env": {{
        "{service_url_env}": "${{{service_url_env}:-http://localhost:8080}}",
        "{auth_env}": "${{{auth_env}}}"
      }}
    }}
  }}
}}"""

MCP_AGENTS_MD = """# MCP_AGENTS.md - Dynamic Agent Registry

This file tracks the generated agents from MCP servers. You can manually modify the 'Tools' list to customize agent expertise.

## Agent Mapping Table

| Name | Description | System Prompt | Tools | Tag | Source MCP |
|------|-------------|---------------|-------|-----|------------|

## Tool Inventory Table

| Tool Name | Description | Tag | Source |
|-----------|-------------|-----|--------|
"""

PIPELINE_YML = """\
name: Build|Upload|Release Python Package

on:
  push:
    branches:
      - 'main'

jobs:
  publish-pypi:
    uses: Knuckles-Team/pipelines/.github/workflows/python_pipeline.yml@latest
    secrets:
      PYPI_API_TOKEN: ${{{{ secrets.PYPI_API_TOKEN }}}}
  publish-docker:
    needs: publish-pypi
    uses: Knuckles-Team/pipelines/.github/workflows/container_pipeline.yml@latest
    secrets:
      DOCKER_REGISTRY: ${{{{ secrets.DOCKER_REGISTRY }}}}
      DOCKER_USERNAME: ${{{{ secrets.DOCKER_USERNAME }}}}
      DOCKER_PASSWORD: ${{{{ secrets.DOCKER_PASSWORD }}}}
      DOCKER_REPOSITORY: ${{{{ secrets.DOCKER_REPOSITORY }}}}
"""

ROOT_AGENTS_MD = """# AGENTS.md

## Tech Stack & Architecture
- Language/Version: Python 3.10+
- Core Libraries: `agent-utilities`, `fastmcp`, `pydantic-ai`
- Key principles: Functional patterns, Pydantic for data validation, asynchronous tool execution.
- Architecture:
    - `api/`: Modular folder for target service client wrappers.
    - `mcp/`: Modular folder for Model Context Protocol action-routed dynamic tool tags.
    - `mcp_server.py`: Main MCP server entry point and tool registration loading.
    - `agent_server.py`: Pydantic AI agent definition and logic.
    - `skills/`: Directory containing modular agent skills (if applicable).

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
"""

AGENTS_MD_PEER = """# AGENTS.md - Known A2A Peer Agents
Last updated: {date}

This file is the local registry of other A2A agents this agent can discover and call.

## Registered A2A Peers

| Name            | Endpoint URL                    | Description                          | Capabilities                     | Auth      | Notes / Last Connected |
|-----------------|---------------------------------|--------------------------------------|----------------------------------|-----------|------------------------|
| SearchMaster    | http://search-agent:9000/a2a    | Advanced web researcher              | web_search, summarize, browse    | none      | {date}             |

*Add new rows manually or let the agent call `register_a2a_peer(...)`.*
"""

USER_MD = """\
# USER.md - About the Human

* **Name:** User
* **Preferred name:** User
* **Timezone:** America/Chicago
* **Location:** Chicago, Illinois
* **Style:** Technical, concise, no fluff
"""

GQL_PY = """\
#!/usr/bin/python
# coding: utf-8
\"\"\"GraphQL API Wrapper for {display_name}.

Provides a GraphQL interface using the `gql` library that mirrors
REST API methods with GraphQL queries and mutations.

Requires: pip install gql[requests]
\"\"\"

import logging
from typing import Dict, Any, Optional, Union, List
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from agent_utilities.core.decorators import require_auth
from agent_utilities.core.exceptions import (
    MissingParameterError,
    ParameterError,
)


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

# ── Main Scaffolding Logic ───────────────────────────────────────────────────


def scaffold(
    package_name: str,
    output_dir: str = ".",
    pkg_types: str = "api_client,mcp,agent,graphql",
    display_name: str = "",
    description: str = "",
    author: str = "Audel Rouhi",
    email: str = "knucklessg1@gmail.com",
    service_url_env: str = "",
    auth_env: str = "",
    doc_urls: str = "",
    in_place: bool = False,
):
    """Scaffold a complete agent-package project."""
    types = [t.strip() for t in pkg_types.split(",")]
    pkg_dir = to_pkg_dir(package_name)
    if not display_name:
        display_name = to_display(package_name)
    if not description:
        description = f"Agent package for {display_name}."
    upper_name = to_upper_env(package_name)
    if not service_url_env:
        service_url_env = f"{upper_name}_URL"
    if not auth_env:
        auth_env = f"{upper_name}_TOKEN"

    # Derived names
    parts = package_name.rsplit("-", 1)
    if len(parts) == 2 and parts[1] in ("mcp", "agent", "api"):
        mcp_cmd = f"{parts[0]}-mcp"
        agent_cmd = f"{parts[0]}-agent"
        mcp_short_name = parts[0]
    else:
        mcp_cmd = f"{package_name}-mcp"
        agent_cmd = f"{package_name}-agent"
        mcp_short_name = package_name

    agent_service_name = agent_cmd
    verify_env = f"{upper_name}_VERIFY"
    api_module_name = "api"
    year = datetime.datetime.now().year
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    mcp_entry = f'{mcp_cmd} = "{pkg_dir}.mcp_server:mcp_server"'
    agent_entry = (
        f'\n{agent_cmd} = "{pkg_dir}.agent_server:agent_server"'
        if "agent" in types
        else ""
    )

    gql_module_name = "gql_client"
    has_graphql = "graphql" in types
    gql_dep = '\ngql = [\n    "gql>=4.0.0"]\n' if has_graphql else "\n"
    all_dep_line = (
        f"{package_name}[mcp,agent,gql,logfire]>=0.1.0"
        if has_graphql
        else "agent-utilities[mcp,agent,logfire]>=0.2.12"
    )
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
        "verify_env": verify_env,
        "mcp_cmd": mcp_cmd,
        "agent_cmd": agent_cmd,
        "agent_service_name": agent_service_name,
        "mcp_short_name": mcp_short_name,
        "api_module_name": api_module_name,
        "gql_module_name": gql_module_name,
        "gql_dep": gql_dep,
        "all_dep_line": all_dep_line,
        "gql_optional_module": gql_optional_module,
        "gql_all_extend": gql_all_extend,
        "year": year,
        "date": date,
        "mcp_entry": mcp_entry,
        "agent_entry": agent_entry,
        "upper_name": upper_name,
    }

    root = Path(output_dir) if in_place else Path(output_dir) / package_name
    pkg = root / pkg_dir
    agent_dir = pkg / "agent"
    agent_dir.mkdir(parents=True, exist_ok=True)

    # ── Root-level files ─────────────────────────────────────────────────
    files = {
        root / "pyproject.toml": PYPROJECT_TOML,
        root / ".bumpversion.cfg": BUMPVERSION_CFG,
        root / ".pre-commit-config.yaml": PRECOMMIT_CONFIG,
        root / ".dockerignore": DOCKERIGNORE,
        root / ".env": ENV_TEMPLATE,
        root / ".gitignore": GITIGNORE,
        root / ".gitattributes": GITATTRIBUTES,
        root / "docker/Dockerfile": DOCKERFILE,
        root / "docker/debug.Dockerfile": DEBUG_DOCKERFILE,
        root / "docker/compose.yml": COMPOSE_YML,
        root / "docker/mcp.compose.yml": MCP_COMPOSE_YML,
        root / "AGENTS.md": ROOT_AGENTS_MD,
        root / "LICENSE": LICENSE_MIT,
        root / "MANIFEST.in": MANIFEST_IN,
        root / "README.md": README_MD,
        root / "requirements.txt": REQUIREMENTS_TXT,
        root / "starship.toml": STARSHIP_TOML,
        root / ".github/workflows/pipeline.yml": PIPELINE_YML,
        root / "CHANGELOG.md": CHANGELOG_MD,
        root / "mkdocs.yml": MKDOCS_YML,
        root / "docs/index.md": DOCS_INDEX_MD,
        root / "docs/overview.md": DOCS_OVERVIEW_MD,
    }

    # ── Package files ────────────────────────────────────────────────────
    files[pkg / "__init__.py"] = INIT_PY
    files[pkg / "auth.py"] = AUTH_PY

    # API modular directory scaffolding
    files[pkg / "api" / "__init__.py"] = API_INIT_PY
    files[pkg / "api" / "api_client_base.py"] = API_CLIENT_BASE
    files[pkg / "api" / "api_client_system.py"] = API_CLIENT_SYSTEM

    # MCP modular directory scaffolding
    files[pkg / "mcp" / "__init__.py"] = MCP_INIT_PY
    files[pkg / "mcp" / "mcp_system.py"] = MCP_SYSTEM_PY

    if "mcp" in types:
        files[pkg / "mcp_server.py"] = MCP_SERVER_PY

    if "agent" in types:
        files[pkg / "agent_server.py"] = AGENT_PY
        files[agent_dir / "IDENTITY.md"] = IDENTITY_MD
        files[agent_dir / "CRON.md"] = CRON_MD
        files[agent_dir / "CRON_LOG.md"] = CRON_LOG_MD
        files[agent_dir / "HEARTBEAT.md"] = HEARTBEAT_MD
        files[agent_dir / "AGENTS.md"] = AGENTS_MD_PEER
        files[agent_dir / "USER.md"] = USER_MD
        files[agent_dir / "mcp_config.json"] = MCP_CONFIG_MD
        files[agent_dir / "MCP_AGENTS.md"] = MCP_AGENTS_MD
        files[pkg / "__main__.py"] = MAIN_PY

        # Create empty icon.png
        (agent_dir / "icon.png").write_bytes(b"")
        # Create chats directory
        (agent_dir / "chats").mkdir(parents=True, exist_ok=True)

    if "graphql" in types:
        files[pkg / f"{gql_module_name}.py"] = GQL_PY

    # Scaffolding flat tests directory
    files[root / "tests" / "conftest.py"] = TESTS_CONFTEST
    files[root / "tests" / "test_api_auth_errors.py"] = TESTS_API_AUTH
    files[root / "tests" / "test_mcp_server_coverage.py"] = TESTS_MCP_SERVER

    # ── Write all files ──────────────────────────────────────────────────
    for path, template in files.items():
        if path.name == "requirements.txt":
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        content = template.format(**ctx)
        path.write_text(content, encoding="utf-8")
        print(f"  ✅ {path.relative_to(root.parent)}")

    import tomllib

    pyproject_content = (root / "pyproject.toml").read_text(encoding="utf-8")
    parsed_toml = tomllib.loads(pyproject_content)
    deps = parsed_toml.get("project", {}).get("dependencies", [])

    req_path = root / "requirements.txt"
    req_path.write_text("\n".join(deps) + "\n", encoding="utf-8")
    print(f"  ✅ {req_path.relative_to(root.parent)}")

    print(f"\n🎉 Scaffolded '{package_name}' at {root.resolve()}")
    print(f"   Package dir: {pkg_dir}/")
    print(f"   Types: {', '.join(types)}")
    if doc_urls:
        print(f"   Doc URLs saved: {doc_urls}")
        print("   → Run skill-graph-builder to generate docs skill.")


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scaffold a complete agent-package project following the jellyfin-mcp gold standard."
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
        default="api_client,mcp,agent,graphql",
        dest="pkg_types",
        type=str,
        help="Comma-separated types: api_client, mcp, agent, graphql (default: all)",
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
        doc_urls=args.doc_urls,
        in_place=args.in_place,
    )
