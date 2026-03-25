#!/usr/bin/env python3
"""
Agent Package Builder — Scaffolds a complete agent-package project.

Generates the full project structure following the jellyfin-mcp gold standard,
including all hidden config files, Docker infrastructure, Python package stubs,
and agent workspace files.
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
{mcp_entry}{agent_entry}

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

[bumpversion:file:Dockerfile]
search = {package_name}[all]>={{current_version}}
replace = {package_name}[all]>={{new_version}}

[bumpversion:file:{pkg_dir}/agent.py]
search = __version__ = "{{current_version}}"
replace = __version__ = "{{new_version}}"

[bumpversion:file:{pkg_dir}/mcp.py]
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
  - repo: https://github.com/psf/black
    rev: 26.1.0
    hooks:
    - id: black
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
        args: ["-L", "ans,linar,nam,tread,ot,"]
        exclude: |
            (?x)^(
              \\./test/.*|
              \\./tests/.*|
              {pkg_dir}/skills/.*-docs/.*
            )$
  - repo: https://github.com/nbQA-dev/nbQA
    rev: 1.9.1
    hooks:
      - id: nbqa-black
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
    && apt-get install -y ripgrep tree fd-find curl nano \\
    && curl -LsSf https://astral.sh/uv/install.sh | sh \\
    && uv pip install --system --upgrade --verbose --no-cache --break-system-packages --prerelease=allow {package_name}[all]>=0.1.0

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
    && apt-get install -y ripgrep tree fd-find curl nano \\
    && curl -LsSf https://astral.sh/uv/install.sh | sh \\
    && uv pip install --system --upgrade --verbose --no-cache --break-system-packages --prerelease=allow .[all]

CMD ["{mcp_cmd}"]
"""

COMPOSE_YML = """\
---
services:
  {agent_service_name}:
    # image: docker.io/knucklessg1/{package_name}:latest
    build:
      context: . # Debug
      dockerfile: debug.Dockerfile
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
      - .env
    environment:
      - "HOST=0.0.0.0"
      - "PORT=9001"
      - "TRANSPORT=stdio"
      - "{service_url_env}=${{{service_url_env}}}"
      - "{auth_env}=${{{auth_env}}}"
      - "PROVIDER=openai"
      - "LLM_BASE_URL=${{LLM_BASE_URL:-http://host.docker.internal:1234/v1}}"
      - "LLM_API_KEY=${{LLM_API_KEY:-llama}}"
      - "MODEL_ID=${{MODEL_ID:-nvidia/nemotron-3-super}}"
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

Dockerfile
debug.Dockerfile
compose.yml
"""

ENV_TEMPLATE = """\
LLM_BASE_URL=http://10.0.0.18:1234/v1
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

# Templates
*.dot             text
*.ejs             text
*.erb             text
*.haml            text
*.handlebars      text
*.hbs             text
*.hbt             text
*.jade            text
*.latte           text
*.mustache        text
*.njk             text
*.phtml           text
*.svelte          text
*.tmpl            text
*.tpl             text
*.twig            text
*.vue             text

# Configs
*.cnf             text
*.conf            text
*.config          text
.editorconfig     text
.env              text
.gitattributes    text
.gitconfig        text
.htaccess         text
*.lock            text -diff
package.json      text eol=lf
package-lock.json text eol=lf -diff
pnpm-lock.yaml    text eol=lf -diff
.prettierrc       text
yarn.lock         text -diff
*.toml            text
*.yaml            text
*.yml             text
browserslist      text
Makefile          text
makefile          text

# Heroku
Procfile          text

# Graphics
*.ai              binary
*.bmp             binary
*.eps             binary
*.gif             binary
*.gifv            binary
*.ico             binary
*.jng             binary
*.jp2             binary
*.jpg             binary
*.jpeg            binary
*.jpx             binary
*.jxr             binary
*.pdf             binary
*.png             binary
*.psb             binary
*.psd             binary
*.svg             text
*.svgz            binary
*.tif             binary
*.tiff            binary
*.wbmp            binary
*.webp            binary

# Audio
*.kar             binary
*.m4a             binary
*.mid             binary
*.midi            binary
*.mp3             binary
*.ogg             binary
*.ra              binary

# Video
*.3gpp            binary
*.3gp             binary
*.as              binary
*.asf             binary
*.asx             binary
*.avi             binary
*.fla             binary
*.flv             binary
*.m4v             binary
*.mng             binary
*.mov             binary
*.mp4             binary
*.mpeg            binary
*.mpg             binary
*.ogv             binary
*.swc             binary
*.swf             binary
*.webm            binary

# Archives
*.7z              binary
*.gz              binary
*.jar             binary
*.rar             binary
*.tar             binary
*.zip             binary

# Fonts
*.ttf             binary
*.eot             binary
*.otf             binary
*.woff            binary
*.woff2           binary

# Executables
*.exe             binary
*.pyc             binary

# RC files
*.*rc             text

# Ignore files
*.*ignore         text
"""

README_MD = """\
# {display_name} - A2A | AG-UI | MCP

![PyPI - Version](https://img.shields.io/pypi/v/{package_name})
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![PyPI - Downloads](https://img.shields.io/pypi/dd/{package_name})
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/{package_name})
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/{package_name})
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/{package_name})
![PyPI - License](https://img.shields.io/pypi/l/{package_name})
![GitHub](https://img.shields.io/github/license/Knuckles-Team/{package_name})

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/{package_name})
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/{package_name})
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/{package_name})
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/{package_name})

![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/{package_name})
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/{package_name})
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/{package_name})
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/{package_name})
![PyPI - Wheel](https://img.shields.io/pypi/wheel/{package_name})
![PyPI - Implementation](https://img.shields.io/pypi/implementation/{package_name})

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

#### Run in HTTP mode:
```bash
export {service_url_env}="http://localhost:8080"
export {auth_env}="your_token"
{mcp_cmd} --transport "http" --host "0.0.0.0" --port "8000"
```

## A2A Agent

### Run A2A Server
```bash
export {service_url_env}="http://localhost:8080"
export {auth_env}="your_token"
{agent_cmd} --provider openai --model-id gpt-4o --api-key sk-...
```

## Docker

### Build

```bash
docker build -t {package_name} .
```

### Run MCP Server

```bash
docker run -d \\
  --name {package_name} \\
  -p 8000:8000 \\
  -e TRANSPORT=http \\
  -e {service_url_env}="http://your-service:8080" \\
  -e {auth_env}="your_token" \\
  knucklessg1/{package_name}:latest
```

### Deploy with Docker Compose

```yaml
services:
  {package_name}:
    image: knucklessg1/{package_name}:latest
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=http
      - {service_url_env}=http://your-service:8080
      - {auth_env}=your_token
    ports:
      - 8000:8000
```

#### Configure `mcp.json` for AI Integration (e.g. Claude Desktop)

```json
{{
  "mcpServers": {{
    "{mcp_short_name}": {{
      "command": "uv",
      "args": [
        "run",
        "--with",
        "{package_name}",
        "{mcp_cmd}"
      ],
      "env": {{
        "{service_url_env}": "http://your-service:8080",
        "{auth_env}": "your_token"
      }}
    }}
  }}
}}
```

## Install Python Package

```bash
python -m pip install {package_name}
```
```bash
uv pip install {package_name}
```

## Repository Owners

<img width="100%" height="180em" src="https://github-readme-stats.vercel.app/api?username=Knucklessg1&show_icons=true&hide_border=true&&count_private=true&include_all_commits=true" />

![GitHub followers](https://img.shields.io/github/followers/Knucklessg1)
![GitHub User's stars](https://img.shields.io/github/stars/Knucklessg1)
"""

INIT_PY = """\
#!/usr/bin/env python
# coding: utf-8

import importlib
import inspect
import warnings
from typing import List

# Suppress RequestsDependencyWarning due to chardet 6.x / requests 2.32.x mismatch
# Centralized here to ensure it runs before any sub-package imports
warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")

__all__: List[str] = []

CORE_MODULES = [
    "{pkg_dir}.{api_module_name}",
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


\"\"\"
{package_name}

{description}
\"\"\"
"""

AUTH_PY = """\
#!/usr/bin/python
# coding: utf-8

import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from agent_utilities.exceptions import AuthError, UnauthorizedError

# TODO: Import your API wrapper class here
# from {pkg_dir}.{api_module_name} import {api_class_name}

_client = None


def get_client():
    \"\"\"Get or create a singleton API client instance.\"\"\"
    global _client
    if _client is None:
        base_url = os.getenv("{service_url_env}", "http://localhost:8080")
        token = os.getenv("{auth_env}", "")
        verify = os.getenv("{verify_env}", "True").lower() in ("true", "1", "yes")

        try:
            # TODO: Uncomment and configure once the API wrapper class is created
            # _client = {api_class_name}(
            #     base_url=base_url,
            #     token=token,
            #     verify=verify,
            # )

            # Placeholder until API wrapper is implemented
            if _client is None:
                session = requests.Session()
                session.headers.update({{"Authorization": f"Bearer {{token}}"}})
                session.verify = verify
                _client = type("Client", (), {{"session": session, "base_url": base_url}})()
        except (AuthError, UnauthorizedError) as e:
            raise RuntimeError(
                f"AUTHENTICATION ERROR: The credentials provided are not valid for '{{base_url}}'. "
                f"Please check your {auth_env} and {service_url_env} environment variables. "
                f"Error details: {{str(e)}}"
            ) from e

    return _client
"""

MCP_PY = """\
#!/usr/bin/python
# coding: utf-8

import os
import sys
import logging
from typing import Optional, List, Dict, Union, Any

from dotenv import load_dotenv, find_dotenv
from fastmcp import FastMCP
from pydantic import Field
from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import create_mcp_server, config
from agent_utilities.utilities import get_logger
from {pkg_dir}.auth import get_client

__version__ = "0.1.0"

# Redirect logging to stderr to prevent MCP stdout corruption
logger = get_logger(name="MCP_Server")
logger.setLevel(logging.INFO)


def register_prompts(mcp: FastMCP):
    @mcp.prompt(
        name="example_prompt", description="Example prompt for {display_name}."
    )
    def example_prompt(query: str) -> str:
        \"\"\"Example prompt.\"\"\"
        return f"Please help with '{{query}}' using {display_name}"


def get_mcp_instance() -> tuple[Any, Any, Any, Any]:
    \"\"\"Initialize and return the {display_name} MCP instance, args, and middlewares.\"\"\"
    load_dotenv(find_dotenv())

    args, mcp, middlewares = create_mcp_server(
        name="{display_name} MCP",
        version=__version__,
        instructions="{display_name} MCP Server",
    )

    # TODO: Register tool groups here with env-var toggles.
    # Pattern: if to_boolean(os.getenv("TOOL_TAG_NAME", "True")): register_tools(mcp)

    register_prompts(mcp)

    for mw in middlewares:
        mcp.add_middleware(mw)

    registered_tags = []
    return mcp, args, middlewares, registered_tags


def mcp_server():
    mcp, args, middlewares, registered_tags = get_mcp_instance()

    # Clean version announcement (stderr or logger preferred)
    print(f"{display_name} MCP v{{__version__}}", file=sys.stderr)
    print("\\nStarting MCP Server", file=sys.stderr)
    print(f"  Transport: {{args.transport.upper()}}", file=sys.stderr)
    print(f"  Auth: {{args.auth_type}}", file=sys.stderr)
    print(f"  Dynamic Tags Loaded: {{len(registered_tags)}}", file=sys.stderr)

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
from agent_utilities.decorators import require_auth
from agent_utilities.exceptions import (
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

        # Adjust the GraphQL endpoint path as needed
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
        \"\"\"Execute a GraphQL query or mutation.

        Args:
            query_str: The GraphQL query or mutation string.
            variables: Optional dictionary of variables for the query.
            operation_name: Optional name of the operation.

        Returns:
            Dict[str, Any]: The raw GraphQL response dictionary.
        \"\"\"
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

    # TODO: Add domain-specific query/mutation methods below.
    # Mirror your REST API methods using GraphQL queries and mutations.
    # Use cursor-based pagination (first/after) for list queries.
    # Example:
    #
    # @require_auth
    # def get_items(self, first: int = 20, after: str = None) -> Dict[str, Any]:
    #     query_str = \"\"\"
    #     query GetItems($first: Int, $after: String) {{
    #         items(first: $first, after: $after) {{
    #             nodes {{ id name }}
    #             pageInfo {{ endCursor hasNextPage }}
    #         }}
    #     }}
    #     \"\"\"
    #     variables = {{"first": first}}
    #     if after:
    #         variables["after"] = after
    #     return self.execute_gql(query_str, variables=variables)
"""

AGENT_PY = """\
#!/usr/bin/python
# coding: utf-8
import os
import logging
import warnings

from agent_utilities import (
    build_system_prompt_from_workspace,
    create_agent_parser,
    create_graph_agent_server,
    initialize_workspace,
    load_identity,
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
DEFAULT_AGENT_SYSTEM_PROMPT = os.getenv(
    "AGENT_SYSTEM_PROMPT",
    meta.get("content") or build_system_prompt_from_workspace(),
)


def agent_template(mcp_url: str = None, mcp_config: str = None, **kwargs):
    \"\"\"Factory function returning the fully initialized graph for execution.\"\"\"
    from agent_utilities import create_graph_agent
    from {pkg_dir}.graph_config import TAG_PROMPTS, TAG_ENV_VARS

    # In-process MCP loading: if no external URL/Config, load the local FastMCP instance
    mcp_toolsets = []
    effective_mcp_url = mcp_url or os.getenv("MCP_URL")
    effective_mcp_config = mcp_config or os.getenv("MCP_CONFIG")

    if not effective_mcp_url and not effective_mcp_config:
        try:
            from {pkg_dir}.mcp_server import get_mcp_instance
            mcp, _, _, _ = get_mcp_instance()
            mcp_toolsets.append(mcp)
            logger.info("{display_name}: Using in-process MCP instance.")
        except (ImportError, Exception) as e:
            logger.warning("{display_name}: Could not load in-process MCP: {{e}}")

    return create_graph_agent(
        tag_prompts=TAG_PROMPTS,
        tag_env_vars=TAG_ENV_VARS,
        mcp_url=effective_mcp_url,
        mcp_config=effective_mcp_config or "",
        mcp_toolsets=mcp_toolsets,
        name=f"{{DEFAULT_AGENT_NAME}} Graph Agent",
        **kwargs
    )


def agent_server():
    logger.info(f"{{DEFAULT_AGENT_NAME}} v{{__version__}}")
    parser = create_agent_parser()
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    # Create graph and config using standardized template
    graph_bundle = agent_template(
        mcp_url=args.mcp_url,
        mcp_config=args.mcp_config,
        provider=args.provider,
        agent_model=args.model_id,
        base_url=args.base_url,
        api_key=args.api_key,
        custom_skills_directory=args.custom_skills_directory,
        debug=args.debug,
        ssl_verify=not args.insecure,
    )

    # Start server using the pre-built graph bundle
    create_graph_agent_server(
        graph_bundle=graph_bundle,
        host=args.host,
        port=args.port,
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

GRAPH_CONFIG_PY = """\
\"\"\"{display_name} graph configuration — tag prompts and env var mappings.

Standardized graph configuration to support hierarchical and specialized domain routing.
\"\"\"

# ── Tag → System Prompt Mapping ──────────────────────────────────────
TAG_PROMPTS: dict[str, str] = {{
    "core": (
        "You are a {display_name} Core specialist. Help users interact with core functionality."
    ),
}}


# ── Tag → Environment Variable Mapping ────────────────────────────────
TAG_ENV_VARS: dict[str, str] = {{
    "core": "CORETOOL",
}}
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
2. **Memory Review** — Read `MEMORY.md` and check for any pending follow-up tasks or action items. List any that are overdue.
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
  "mcpServers": {{}}
}}"""
MEMORY_MD = """\
# MEMORY.md - Long-term Memory
Last updated: {date}

This file stores important decisions, user preferences, and historical outcomes.
The agent should read this if the user asks "remember when" or similar.

## Log of Important Events
- [{date}] Workspace initialized with advanced agent features.
"""

# ── AGENTS.md (Root for coding agents) ────────────────────────────────

ROOT_AGENTS_MD = """# AGENTS.md

## Tech Stack & Architecture
- Language/Version: Python 3.10+
- Core Libraries: `agent-utilities`, `fastmcp`, `pydantic-ai`
- Key principles: Functional patterns, Pydantic for data validation, asynchronous tool execution.
- Architecture:
    - `mcp.py`: Main MCP server entry point and tool registration.
    - `agent.py`: Pydantic AI agent definition and logic.
    - `skills/`: Directory containing modular agent skills (if applicable).
    - `agent/`: Internal agent logic and prompt templates.

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
- MCP Entry Point → `mcp.py`
- Agent Entry Point → `agent.py`
- Source Code → {pkg_dir}/
- Skills → `skills/` (if exists)

### File Tree
```text
├── .bumpversion.cfg
├── .dockerignore
├── .env
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── Dockerfile
├── LICENSE
├── MANIFEST.in
├── README.md
├── compose.yml
├── debug.Dockerfile
├── {pkg_dir}
│   ├── __init__.py
│   ├── agent.py
│   ├── auth.py
│   ├── mcp.py
│   └── agent/
├── pyproject.toml
└── requirements.txt
```

## Code Style & Conventions
**Always:**
- Use `agent-utilities` for common patterns (e.g., `create_mcp_server`, `create_agent`).
- Define input/output models using Pydantic.
- Include descriptive docstrings for all tools (they are used as tool descriptions for LLMs).
- Check for optional dependencies using `try/except ImportError`.

**Good example:**
```python
from agent_utilities import create_mcp_server
from mcp.server.fastmcp import FastMCP

mcp = create_mcp_server("my-agent")

@mcp.tool()
async def my_tool(param: str) -> str:
    \"\"\"Description for LLM.\"\"\"
    return f"Result: {{param}}"
```

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
- Major refactors of `mcp.py` or `agent.py`.
- Deleting or renaming public tool functions.

**Never do:**
- Commit `.env` files or secrets.
- Modify `agent-utilities` or `universal-skills` files from within this package.

## When Stuck
- Propose a plan first before making large changes.
- Check `agent-utilities` documentation for existing helpers.
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

# ── Main scaffolding logic ───────────────────────────────────────────────────


def scaffold(
    package_name: str,
    output_dir: str = ".",
    pkg_types: str = "api_wrapper,mcp,agent,graphql",
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
    mcp_cmd = (
        f"{package_name.split('-')[0]}-mcp"
        if "-" in package_name
        else f"{package_name}-mcp"
    )
    # Try to derive a short name: use the first word if it has a suffix like -mcp/-agent
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
    api_module_name = (
        f"{pkg_dir.split('_')[0]}_api" if "_" in pkg_dir else f"{pkg_dir}_api"
    )
    api_class_name = (
        "".join(w.capitalize() for w in api_module_name.replace("_api", "").split("_"))
        + "Api"
    )
    year = datetime.datetime.now().year
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Entry point lines
    mcp_entry = f'{mcp_cmd} = "{pkg_dir}.mcp:mcp_server"'
    agent_entry = (
        f'\n{agent_cmd} = "{pkg_dir}.agent:agent_server"' if "agent" in types else ""
    )

    # GraphQL-conditional template placeholders
    gql_module_name = (
        f"{pkg_dir.split('_')[0]}_gql" if "_" in pkg_dir else f"{pkg_dir}_gql"
    )
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
        "api_class_name": api_class_name,
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
        root / "Dockerfile": DOCKERFILE,
        root / "debug.Dockerfile": DEBUG_DOCKERFILE,
        root / "compose.yml": COMPOSE_YML,
        root / "AGENTS.md": ROOT_AGENTS_MD,
        root / "LICENSE": LICENSE_MIT,
        root / "MANIFEST.in": MANIFEST_IN,
        root / "README.md": README_MD,
        root / "requirements.txt": REQUIREMENTS_TXT,
    }

    # ── Package files ────────────────────────────────────────────────────
    files[pkg / "__init__.py"] = INIT_PY
    files[pkg / "auth.py"] = AUTH_PY

    if "mcp" in types:
        files[pkg / "mcp_server.py"] = MCP_PY

    if "agent" in types:
        files[pkg / "agent_server.py"] = AGENT_PY
        files[pkg / "graph_config.py"] = GRAPH_CONFIG_PY
        files[agent_dir / "IDENTITY.md"] = IDENTITY_MD
        files[agent_dir / "CRON.md"] = CRON_MD
        files[agent_dir / "CRON_LOG.md"] = CRON_LOG_MD
        files[agent_dir / "HEARTBEAT.md"] = HEARTBEAT_MD
        files[agent_dir / "MEMORY.md"] = MEMORY_MD
        files[agent_dir / "AGENTS.md"] = AGENTS_MD_PEER
        files[agent_dir / "USER.md"] = USER_MD
        files[agent_dir / "mcp_config.json"] = MCP_CONFIG_MD
        files[pkg / "__main__.py"] = MAIN_PY

        # Create empty icon.png
        (agent_dir / "icon.png").write_bytes(b"")
        # Create chats directory
        (agent_dir / "chats").mkdir(parents=True, exist_ok=True)

    if "graphql" in types:
        files[pkg / f"{gql_module_name}.py"] = GQL_PY

    # ── Write all files ──────────────────────────────────────────────────
    for path, template in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        content = template.format(**ctx)
        path.write_text(content, encoding="utf-8")
        print(f"  ✅ {path.relative_to(root.parent)}")

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
        default="api_wrapper,mcp,agent,graphql",
        dest="pkg_types",
        type=str,
        help="Comma-separated types: api_wrapper, mcp, agent, graphql (default: all)",
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
