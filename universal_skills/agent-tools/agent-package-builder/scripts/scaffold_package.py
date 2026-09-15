#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Connector Builder — scaffolds a connector package on agent-connector-sdk.

RF-ADR-009 retarget (workspace phase 7 / lane BUILDER-RETARGET, W2): a scaffolded
package depends on ``agent-connector-sdk`` and ``epistemic-graph`` only (never
``agent-utilities``), builds its MCP server with the SDK's ``create_mcp_server`` +
``register_tool_surface``, serves its skills/prompts/ontology/shapes/manifest as
native MCP primitives through ``ConnectorContent``, declares credentials as
``env://``/``openbao://`` references, carries a ``connector_manifest.yml`` with a
valid ``sync`` preset, publishes docs from ``pages/`` (no ``/docs``), and wires
CI + pre-commit to consume the shared hook repository (``Knuckles-Team/pipelines``)
once it publishes the gate bundle (RF-ADR-009 section 8's "gate-script
duplication" item) rather than copying gate scripts into every package.

See PARITY_MANIFEST.md (sibling of SKILL.md) for the definitive generated-file
contract.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by unequipped runs
    print(
        "Error: scaffold_package.py needs PyYAML to render connector_manifest.yml.\n"
        "Install it with: pip install 'universal-skills[agent-package-builder]'"
    )
    raise SystemExit(1) from exc

__all__ = [
    "build_context",
    "scaffold",
    "to_display",
    "to_pkg_dir",
    "to_upper_env",
]

# ── Utility ──────────────────────────────────────────────────────────────────


def to_pkg_dir(name: str) -> str:
    """Convert a kebab-case package name to its underscore Python package dir."""
    return name.replace("-", "_")


def to_display(name: str) -> str:
    """Convert kebab-case to Title Case display name."""
    return " ".join(w.capitalize() for w in name.split("-"))


def to_upper_env(name: str) -> str:
    """Convert kebab-case to UPPER_SNAKE env prefix."""
    return name.replace("-", "_").upper()


_PLACEHOLDER_RE = re.compile(r"@@([a-z0-9_]+)@@")


def render(template: str, **values: object) -> str:
    """Substitute ``@@name@@`` placeholders; unlike ``str.format`` this never
    collides with the literal ``{}``/``$`` a Python, JSON, YAML or shell
    template legitimately contains."""

    def _sub(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise KeyError(f"unbound placeholder @@{key}@@ in template")
        return str(values[key])

    return _PLACEHOLDER_RE.sub(_sub, template)


def _write_generated_text(path: Path, content: str) -> bool:
    """Create a generated text file without overwriting an existing file.

    A scaffold may be re-run in a checkout that already contains operator or
    project-owned files. Matching content is already in the desired state;
    different content is deliberately preserved so a generator update cannot
    destroy local work. The return value tells the caller whether a file was
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


def _write_generated_json(path: Path, document: object) -> bool:
    return _write_generated_text(
        path, json.dumps(document, indent=2, sort_keys=True) + "\n"
    )


# ── Context ──────────────────────────────────────────────────────────────────

GITHUB_ORG = "Knuckles-Team"
SDK_MIN_VERSION = "0.1.0"
EG_MIN_VERSION = "2.23.0"
#: Knuckles-Team/pipelines commit this scaffold's Pages workflow call and
#: readiness contract were proved against (pipelines `main`, 2026-09-13).
#: pipelines must be pushed to this ref before a generated repository's Pages
#: workflow can resolve it.
PIPELINES_SHA = "2d9681bfdbfc8d99d526769e36610864ce773630"
#: repository-manager commit the docs-readiness preflight contract
#: (`_content_source`, `_input_preflight`) was proved against (main,
#: 2026-09-13) — informational; not referenced by a generated file.
REPOSITORY_MANAGER_SHA = "8f1b17fb0295c3170f3c1a0d98182a409bb25072"

#: Outbound auth modes the generated ``api_client.py`` can build
#: (agent-connector-sdk ``auth.static``/``auth.oidc``/``auth.delegation``).
AUTH_MODES = ("bearer", "basic", "api_key", "client_credentials", "delegated")
#: ``mcp_tool`` pagination styles ``preset_pagination`` covers.
PAGINATION_MODES = ("cursor", "page", "offset")
DEFAULT_PAGE_SIZE = 100


def _openapi_hint(openapi_path: str | None) -> dict[str, str]:
    """The base URL and one list operation's path from a small OpenAPI document.

    Best-effort: only ``servers[0].url`` and the first ``GET`` path are read.
    Returns an empty mapping when ``openapi_path`` is not given.
    """
    if not openapi_path:
        return {}
    document = yaml.safe_load(Path(openapi_path).read_text(encoding="utf-8")) or {}
    servers = document.get("servers") or []
    base_url = servers[0].get("url") if servers and isinstance(servers[0], dict) else None
    paths = document.get("paths") or {}
    list_path = next(
        (path for path, ops in paths.items() if isinstance(ops, dict) and "get" in ops),
        None,
    )
    hint: dict[str, str] = {}
    if base_url:
        hint["base_url"] = str(base_url)
    if list_path:
        hint["list_path"] = str(list_path)
    return hint


def build_context(
    package_name: str,
    *,
    display_name: str | None = None,
    description: str | None = None,
    domain: str = "reader",
    auth_mode: str = "bearer",
    pagination: str = "cursor",
    openapi: str | None = None,
) -> dict[str, str]:
    """Derive every template placeholder from the package name and options."""
    if auth_mode not in AUTH_MODES:
        raise ValueError(f"auth_mode must be one of {AUTH_MODES}")
    if pagination not in PAGINATION_MODES:
        raise ValueError(f"pagination must be one of {PAGINATION_MODES}")
    pkg_dir = to_pkg_dir(package_name)
    display = display_name or to_display(package_name)
    domain = domain.strip().lower().replace("-", "_") or "reader"
    tool_name = f"{pkg_dir}_{domain}"
    doc_type = f"{pkg_dir}_item"
    resource_name = "".join(part.capitalize() for part in pkg_dir.split("_")) + "Item"
    hint = _openapi_hint(openapi)
    return {
        "package_name": package_name,
        "pkg_dir": pkg_dir,
        "display_name": display,
        "description": description or f"{display} connector on agent-connector-sdk.",
        "domain": domain,
        "tool_name": tool_name,
        "doc_type": doc_type,
        "resource_name": resource_name,
        "mcp_cmd": f"{package_name}-mcp",
        "short_env": to_upper_env(pkg_dir),
        "github_org": GITHUB_ORG,
        "year": str(datetime.date.today().year),
        "sdk_min_version": SDK_MIN_VERSION,
        "eg_min_version": EG_MIN_VERSION,
        "pipelines_sha": PIPELINES_SHA,
        "auth_mode": auth_mode,
        "pagination": pagination,
        "page_size": str(DEFAULT_PAGE_SIZE),
        "base_url": hint.get("base_url", "https://api.example.invalid"),
        "list_path": hint.get("list_path", f"/{domain}"),
    }


def _pagination_preset_fields(pagination: str, page_size: int) -> dict[str, object]:
    """The pagination-specific preset fields, matching
    ``agent_connector_sdk.http.pagination.preset_pagination`` exactly (the tool
    returns a ``ToolPage``, whose JSON shape this mirrors)."""
    if pagination == "cursor":
        return {
            "pagination": "cursor",
            "cursor_param": "cursor",
            "cursor_path": "next_cursor",
            "more_path": "has_more",
        }
    return {
        "pagination": pagination,
        "page_param": "page" if pagination == "page" else "offset",
        "page_size_param": "page_size" if pagination == "page" else "limit",
        "page_size": page_size,
        "page_kind": "number" if pagination == "page" else "offset",
    }


def _preset_dict(ctx: dict[str, str]) -> dict[str, object]:
    """The one ``mcp_tool`` sync preset the ``@@tool_name@@`` tool serves.

    Shared verbatim between ``connectors/mcp_source_presets.json`` (the
    structural preset declaration ``agent_connector_sdk.manifest.loader``
    cross-checks the manifest against) and the manifest ``sync[0].raw`` field
    (what ``McpToolSourceAdapter.from_sync_spec`` actually extracts with).
    ``params_style: "args"`` and no ``action`` means the tool call passes the
    pagination parameter straight through as a keyword argument — exactly what
    ``@@pkg_dir@@/mcp/mcp_@@domain@@.py`` declares.
    """
    return {
        "server": ctx["package_name"],
        "tool": ctx["tool_name"],
        "action": "",
        "params_style": "args",
        "records_path": "items",
        "id_field": "id",
        "title_field": "title",
        "text_field": "text",
        "doc_type": ctx["doc_type"],
        **_pagination_preset_fields(ctx["pagination"], int(ctx["page_size"])),
    }


# ── Root text templates ──────────────────────────────────────────────────────

PYPROJECT_TOML = """\
[build-system]
requires = ["setuptools>=80.9.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "@@package_name@@"
version = "0.1.0"
description = "@@description@@"
readme = "README.md"
requires-python = ">=3.12,<3.15"
license = "MIT"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
]
# RF-ADR-009 phase 7: a connector depends on agent-connector-sdk and the
# epistemic-graph client only. It must never depend on agent-utilities or any
# later-phase package; the phase-direction check fails the push.
dependencies = [
    "agent-connector-sdk>=@@sdk_min_version@@,<1.0.0",
    "epistemic-graph>=@@eg_min_version@@,<3.0.0",
]

[[project.authors]]
name = "Repository Maintainers"

[project.urls]
Homepage = "https://github.com/@@github_org@@/@@package_name@@"
Documentation = "https://knuckles-team.github.io/@@package_name@@/"

[project.scripts]
@@mcp_cmd@@ = "@@pkg_dir@@.mcp_server:mcp_server"

[tool.setuptools]
include-package-data = true

[tool.setuptools.packages.find]
where = ["."]
include = ["@@pkg_dir@@*"]

[tool.setuptools.package-data]
@@pkg_dir@@ = ["py.typed"]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "RUF"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.12"
ignore_missing_imports = true
check_untyped_defs = true

[dependency-groups]
test = ["pytest>=9.1.1", "pytest-asyncio>=1.4.0", "pytest-timeout>=2.4.0"]
# universal-skills is a dev-only readiness-generation dependency: it is the
# canonical agent-readiness builder repository-manager's docs_readiness also
# resolves (universal_skills.agent_readiness.generate). Never a runtime
# dependency of this connector.
docs = ["mkdocs-material==9.7.7", "universal-skills[agent-package-builder]>=1.3.1,<2.0.0"]

[tool.uv]
default-groups = ["test"]

[tool.vulture]
ignore_names = ["request", "config"]
"""

BUMPVERSION_CFG = """\
[bumpversion]
current_version = 0.1.0
commit = True
tag = True

[bumpversion:file:pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file:README.md]
search = Version: {current_version}
replace = Version: {new_version}

[bumpversion:file:docker/Dockerfile]
search = @@package_name@@>={current_version}
replace = @@package_name@@>={new_version}

[bumpversion:file:@@pkg_dir@@/mcp_server.py]
search = __version__ = "{current_version}"
replace = __version__ = "{new_version}"
"""

# ── Pre-commit: standard hooks pinned to reviewed revisions, plus the shared
# hook repository (SHARED-HOOKS lane) for the gate-script categories RF-ADR-009
# section 8 lists for consolidation. Per operator ruling D9: reference the
# shared hooks by their published ids at ``rev: main`` (pipelines has no
# per-release tags yet); do not copy the gate scripts themselves into this
# package.
PRECOMMIT_CONFIG = """\
default_language_version:
  python: python3
default_install_hook_types: [pre-commit, pre-push]
# Fast checks at pre-commit; the test suite and anything that needs a synced
# environment run at pre-push/manual only.
default_stages: [pre-commit]
ci:
  autofix_prs: true
  autoupdate_commit_msg: '[pre-commit.ci] pre-commit suggestions'
  autoupdate_schedule: 'monthly'

repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: 3e8a8703264a2f4a69428a0aa4dcb512790b2c8c # v6.0.0
  hooks:
  - id: check-added-large-files
    args: ["--maxkb=2000"]
  - id: check-ast
  - id: check-yaml
    args: ["--unsafe"]
  - id: check-toml
  - id: check-json
  - id: fix-byte-order-marker
  - id: check-merge-conflict
  - id: detect-private-key
  - id: trailing-whitespace
  - id: end-of-file-fixer
  - id: no-commit-to-branch
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: 6fec9b7edb08fd9989088709d864a7826dc74e80 # v0.15.12
  hooks:
  - id: ruff-check
    args: ["--fix"]
  - id: ruff-format
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: fc0f09a29bb495f4a91f00266155d6282d52485d # v1.20.2
  hooks:
  - id: mypy
    additional_dependencies: [pydantic==2.13.4, types-PyYAML==6.0.12.20260518]
    args: ["--ignore-missing-imports"]
- repo: https://github.com/astral-sh/uv-pre-commit
  rev: 6a280ba12b7901e47757c868c8c13c6a624c9ecb # 0.11.7
  hooks:
  - id: uv-lock
    args: ["--check"]
# ── Shared workspace gate bundle (RF-ADR-009 section 8 "gate-script
# duplication"). complexity, KISS diff-scope, duplication, secret-history,
# security sanitizer, tracked-privacy, root-hygiene and dependency-audit are
# consolidated into ONE hook repository so 72 connectors never receive
# copies; ids match pipelines' published .pre-commit-hooks.yaml exactly
# (operator ruling D9: rev: main until pipelines cuts per-release tags) —
# do not vendor the gate scripts here.
- repo: https://github.com/@@github_org@@/pipelines
  rev: main
  hooks:
  - id: complexity-staged
  - id: kiss-staged
  - id: dupehound-changed
  - id: secret-history
  - id: security-sanitizer
  - id: tracked-privacy
  - id: root-hygiene
  - id: dependency-audit
  - id: check-orphan-modules
- repo: local
  hooks:
  - id: connector-manifest-consistency
    name: connector manifest agrees with its presets and pinned fingerprints
    entry: uv run --frozen python -c "from agent_connector_sdk.manifest.loader import require_valid_connector_package; from pathlib import Path; require_valid_connector_package(Path('.'))"
    language: system
    files: ^(connector_manifest\\.yml|connectors/.*\\.json)$
    pass_filenames: false
  - id: pytest
    name: pytest (full suite)
    entry: uv run --frozen python -m pytest -q
    language: system
    types: [python]
    pass_filenames: false
    always_run: true
    stages: [pre-push, manual]
"""

DOCKERFILE = """\
# syntax=docker/dockerfile:1
# One runtime image: the MCP server plus its mandatory agent-connector-sdk +
# epistemic-graph client dependency closure. There is no separate agent-runtime
# target here — agent orchestration is agent-utilities' job (a later workspace
# phase this package must never depend on); this image only serves MCP.
#
#   docker build -t @@package_name@@:local .
FROM python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de AS builder
COPY --from=ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \\
    UV_LINK_MODE=copy \\
    UV_SYSTEM_PYTHON=1 \\
    UV_HTTP_TIMEOUT=3600
RUN --mount=type=cache,target=/root/.cache/uv \\
    uv pip install --system --upgrade --break-system-packages @@package_name@@>=0.1.0

FROM python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de
ARG HOST=127.0.0.1
ARG PORT=8000
ARG TRANSPORT="stdio"
ARG AUTH_TYPE="none"
ENV HOST=${HOST} \\
    PORT=${PORT} \\
    TRANSPORT=${TRANSPORT} \\
    AUTH_TYPE=${AUTH_TYPE} \\
    PYTHONUNBUFFERED=1
COPY --from=builder /usr/local /usr/local
CMD ["@@mcp_cmd@@"]
"""

DEBUG_DOCKERFILE = """\
FROM python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de
COPY --from=ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a /uv /uvx /bin/
ENV PYTHONUNBUFFERED=1 \\
    UV_SYSTEM_PYTHON=1 \\
    UV_HTTP_TIMEOUT=3600
WORKDIR /app
COPY . /app
RUN uv pip install --system --upgrade --no-cache --break-system-packages .
CMD ["@@mcp_cmd@@"]
"""

MCP_COMPOSE_YML = """\
version: '3.8'

services:
  @@package_name@@-mcp:
    image: "${MCP_IMAGE:?set-MCP_IMAGE-to-image@sha256-digest}"
    container_name: @@package_name@@-mcp
    hostname: @@package_name@@-mcp
    restart: always
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
      - AUTH_TYPE=${AUTH_TYPE:?set-AUTH_TYPE-to-a-configured-auth-provider}
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

# --- .env.example client blocks, one per --auth mode (agent_connector_sdk's
# http/tls/auth layer; api_client.py's _auth() reads exactly these settings).
_CLIENT_ENV_BLOCKS: dict[str, str] = {
    "bearer": """\
@@short_env@@_URL=@@base_url@@
# @@short_env@@_TOKEN_REF=env://@@short_env@@_TOKEN
# @@short_env@@_TOKEN_REF=openbao://apps/@@package_name@@#TOKEN
""",
    "basic": """\
@@short_env@@_URL=@@base_url@@
@@short_env@@_USERNAME=changeme
# @@short_env@@_PASSWORD_REF=env://@@short_env@@_PASSWORD
# @@short_env@@_PASSWORD_REF=openbao://apps/@@package_name@@#PASSWORD
""",
    "api_key": """\
@@short_env@@_URL=@@base_url@@
# @@short_env@@_API_KEY_REF=env://@@short_env@@_API_KEY
# @@short_env@@_API_KEY_REF=openbao://apps/@@package_name@@#API_KEY
""",
    "client_credentials": """\
@@short_env@@_URL=@@base_url@@

# --- OAuth 2.0 client credentials (agent_connector_sdk.auth.oidc) ---
# OIDC_ISSUER=https://idp.example.invalid/realms/fleet
OIDC_CLIENT_ID=changeme
# OIDC_CLIENT_SECRET_REF=env://OIDC_CLIENT_SECRET
# OIDC_CLIENT_SECRET_REF=openbao://apps/@@package_name@@#OIDC_CLIENT_SECRET
OIDC_AUDIENCE=@@package_name@@-api
""",
    "delegated": """\
@@short_env@@_URL=@@base_url@@

# --- Delegated (on-behalf-of) auth (agent_connector_sdk.auth.delegation) ---
ENABLE_DELEGATION=true
OIDC_TOKEN_URL=https://idp.example.invalid/realms/fleet/protocol/openid-connect/token
OIDC_CLIENT_ID=changeme
# OIDC_CLIENT_SECRET_REF=env://OIDC_CLIENT_SECRET
# OIDC_CLIENT_SECRET_REF=openbao://apps/@@package_name@@#OIDC_CLIENT_SECRET
AUDIENCE=@@package_name@@-api
DELEGATED_SCOPES=api
""",
}

ENV_EXAMPLE = """\
# ==============================================================================
# @@display_name@@ environment configuration
# ==============================================================================
# Configuration is read only through agent_connector_sdk.config.setting().
# A credential-shaped key (*_SECRET, *_PASSWORD, *_TOKEN, *_API_KEY,
# *_PRIVATE_KEY) must hold an env:// or openbao:// secret reference, never a
# raw value (agent_connector_sdk.config.load_config enforces this).

# --- MCP server ---
HOST=127.0.0.1
PORT=8000
TRANSPORT=stdio # options: stdio, streamable-http, sse
AUTH_TYPE=none # a listener outside loopback requires configured authentication
MCP_TOOL_MODE=intent # options: condensed, verbose, both, intent

# --- @@display_name@@ API client (agent_connector_sdk.http/tls/auth;
# @@pkg_dir@@.api_client.build_client resolves these at composition time) ---
@@client_env_block@@
# --- TLS profile (agent_connector_sdk.tls.resolve; service="@@pkg_dir@@") ---
# @@short_env@@_CA_BUNDLE_REF=env://@@short_env@@_CA_BUNDLE
# @@short_env@@_TLS_PROFILE=default

# --- OpenBao (only needed when a reference above uses openbao://) ---
# OPENBAO_ADDR=https://openbao.example.invalid:8200
# OPENBAO_TOKEN_REF=env://OPENBAO_TOKEN
"""

PYTEST_INI = """\
[pytest]
timeout = 60
asyncio_mode = auto
testpaths = tests
"""

CODESPELLIGNORE = """\
# codespell ignore words list
uv
mcp
pydantic
fastmcp
openbao
pre-commit
setuptools
pyproject
bumpversion
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

Copyright (c) @@year@@ Repository Maintainers

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

CHANGELOG_MD = """\
# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - @@year@@-01-01

### Added

- Initial scaffold on `agent-connector-sdk`.
"""

MANIFEST_IN = """\
include LICENSE
include README.md
include connector_manifest.yml
recursive-include @@pkg_dir@@ *.py *.json *.md *.yaml *.yml
recursive-include skills *.md
recursive-include prompts *.json
recursive-include ontology *.ttl
recursive-include connectors *.json
"""

GITIGNORE = """\
__pycache__/
*.py[codz]
*$py.class
*.so

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
*.egg-info/
.installed.cfg
*.egg

htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
.hypothesis/
.pytest_cache/

.env
.envrc
.venv
env/
venv/

/site
.mypy_cache/
.dmypy.json
dmypy.json
.ruff_cache/
"""

GITATTRIBUTES = """\
* text=auto
*.py text diff=python
*.md text diff=markdown eol=lf
*.json text
*.yml text
*.yaml text
LICENSE text
"""

DOCKERIGNORE = """\
.git/
.venv/
__pycache__/
*.pyc
tests/
docker/
.github/
.pre-commit-config.yaml
"""

ROOT_AGENTS_MD = """\
# AGENTS.md

Guide for agents and humans working in **@@package_name@@**, an MCP connector
built on [agent-connector-sdk](https://github.com/@@github_org@@/agent-connector-sdk)
(RF-ADR-009, workspace phase 7). Published documentation is the GitHub Pages
site built from `pages/`; there is no `/docs`.

## What this repository owns

| Owns | Must not own |
|---|---|
| The `@@tool_name@@` domain MCP tool(s) under `@@pkg_dir@@/mcp/` | agent orchestration, LLM calls |
| Content: `skills/`, `prompts/`, `ontology/` (+ `ontology/shapes/`), `connector_manifest.yml`, `connectors/` sync presets | the pack/record schema, ontology reasoning and storage (epistemic-graph owns those) |
| Serving that content as native MCP primitives (`ConnectorContent`) | a second export/sync channel outside MCP |

**Dependencies are `agent-connector-sdk` and `epistemic-graph` only.** Never
add `agent-utilities` or any later-phase package; the phase-direction check
fails the push.

## Layout

| Path | Contents |
|---|---|
| `@@pkg_dir@@/api_client.py` | the governed API client (`agent_connector_sdk.http`/`tls`/`auth` only) — point `_auth()` and `@@short_env@@_URL` at the real vendor API |
| `@@pkg_dir@@/mcp_server.py` | builds the server: `create_mcp_server` + `register_tool_surface` + `ConnectorContent` |
| `@@pkg_dir@@/mcp/mcp_@@domain@@.py` | the `@@tool_name@@` tool — calls `api_client.build_client()`; replace `_LIST_PATH` and the response field names with the vendor's real shape |
| `@@pkg_dir@@/credentials.py` | wires `env://`/`openbao://` secret references through `agent_connector_sdk.credentials` for ad hoc use |
| `skills/`, `prompts/`, `ontology/`, `connectors/` | served as MCP primitives by `ConnectorContent`; see `connector_manifest.yml` |
| `connector_manifest.yml` | the Connector Ontology Manifest — resources, identity, `schema_mappings`, one `sync` preset |
| `scripts/pin_tool_schema.py` | run after `uv sync` (and whenever the tool's parameters change) to pin the live tool schema fingerprint the manifest's `sync[0].tool_schema_sha256` and `connectors/tool_schema_fingerprints.json` both pin |
| `pages/` | hand-written Pages sources (`mkdocs.yml` sets `docs_dir: pages`) |

## Commands

```bash
uv sync                                          # the project environment (Python 3.12)
python scripts/pin_tool_schema.py                # required once after uv sync
uv run --frozen python -m pytest -q              # tests (manifest, MCP server, conformance)
pre-commit run --all-files                       # commit-stage suite
pre-commit run --all-files --hook-stage pre-push # push-stage suite
```

## Rules

- **Worktrees, not the shared checkout**, for concurrent development:
  `git worktree add <path> -b <branch> main`. Never use the harness's
  `EnterWorktree` or `isolation: "worktree"` against a shared multi-worktree
  repository, and never `git stash` there (the stash is shared by every
  worktree).
- **Stage explicit paths.** Never `git add -A` or `git add .`; review
  `git diff --cached` before committing.
- **Full green, no suppressions.** No `noqa`, `type: ignore`, skips, xfails,
  baselines or ratchets. No `--no-verify`.
- **Credentials are references, never values.** `*_TOKEN`, `*_SECRET`,
  `*_PASSWORD`, `*_API_KEY` and `*_PRIVATE_KEY` settings must hold an
  `env://NAME` or `openbao://mount/path#field` reference; `.env` is never
  generated or committed.
- **Fail closed.** A malformed manifest, a drifted live tool schema, or a
  missing credential reference all raise; nothing degrades to permissive.
- **No version suffixes** in names (`StorageKernel`, not `StorageKernelV1`) and
  no compatibility shims.

## Known packaging limitation

`skills/`, `prompts/`, `ontology/` and `connectors/` live at the repository
root (matching `agent_connector_sdk.mcp.content.ConnectorContent`'s package
layout and the SDK's own `tests/fixture_package`), so an editable install
(`uv sync`, `pip install -e .`) serves them correctly because `@@pkg_dir@@`'s
`__file__`-relative path still resolves to the checkout. A non-editable wheel
install does not carry root-level directories into `site-packages`; packaging
those directories as installable data is tracked as a follow-up rather than
solved here (the SDK's own fixture has the same property).
"""

README_MD = """\
# @@display_name@@

An MCP connector on [agent-connector-sdk](https://github.com/@@github_org@@/agent-connector-sdk).

*Version: 0.1.0*

> **Documentation** — installation, usage and deployment are maintained in the
> [official documentation](https://knuckles-team.github.io/@@package_name@@/).

@@description@@

## Key features

- **One native MCP surface.** Tools, skills, prompts, ontology, SHACL shapes
  and the connector manifest are all served as native MCP primitives
  (`tools/list`, `skill://`, `prompts/list`, `ontology://`, `shapes://`,
  `manifest://connector`) — there is no second export channel.
- **`agent-connector-sdk` native.** The server, tool surface, credential
  references and manifest schema come from the SDK; this package adds only
  its own domain tools and content.
- **Governed sync.** `connector_manifest.yml` declares a `sync` preset the
  agent-connector-sdk sync runner extracts through, pinned by
  `tool_schema_sha256` so a drifted live tool fails closed instead of silently
  changing what gets ingested.

## Installation

```bash
uvx --from @@package_name@@ @@mcp_cmd@@   # run without installing
python -m pip install @@package_name@@    # or install normally
```

## Usage

```bash
# Local stdio (for IDEs)
@@mcp_cmd@@

# Networked streamable-http
@@mcp_cmd@@ --transport streamable-http --host 127.0.0.1 --port 8000
```

```json
{
  "mcpServers": {
    "@@package_name@@": {
      "command": "@@mcp_cmd@@",
      "args": [],
      "env": {"MCP_TOOL_MODE": "intent"}
    }
  }
}
```

Credentials are configured as `env://` or `openbao://` references — see
`.env.example` and `@@pkg_dir@@/credentials.py`. `.env` is never generated or
committed.

## Documentation

Full documentation: <https://knuckles-team.github.io/@@package_name@@/>
"""

MKDOCS_YML = """\
# Theme, palette and markdown_extensions come from the shared Knuckles-Team/
# pipelines Pages theme (templates/mkdocs-theme/base.mkdocs.yml), inherited at
# build time by the pages_pipeline.yml reusable workflow's INHERIT: injection
# (shared_theme_enabled: true in .github/workflows/pages.yml) — this file is
# reduced to its own content manifest and never hand-copies that theme.
site_name: @@package_name@@
site_description: @@description@@
site_url: https://knuckles-team.github.io/@@package_name@@/
repo_url: https://github.com/@@github_org@@/@@package_name@@
docs_dir: pages
strict: true
nav:
  - Overview: index.md
  - Installation: installation.md
  - Usage: usage.md
  - Deployment: deployment.md
  - Concepts: concepts.md
"""

PAGES_INDEX_MD = """\
# @@display_name@@

@@description@@

Built on [agent-connector-sdk](https://github.com/@@github_org@@/agent-connector-sdk):
one MCP server, its content served as native MCP primitives, and a
`connector_manifest.yml` the agent-connector-sdk sync runner extracts through.
"""

PAGES_INSTALLATION_MD = """\
# Installation

```bash
uvx --from @@package_name@@ @@mcp_cmd@@   # run without installing
python -m pip install @@package_name@@    # or install normally
```

Requires Python 3.12–3.14.
"""

PAGES_USAGE_MD = """\
# Usage

```bash
@@mcp_cmd@@                                                    # local stdio
@@mcp_cmd@@ --transport streamable-http --host 127.0.0.1 --port 8000
```

The `@@tool_name@@` tool calls `@@pkg_dir@@/api_client.py`'s governed HTTP
client and returns an `agent_connector_sdk.http.pagination.ToolPage`. It
takes one pagination parameter, `@@pagination@@` (chosen by `--pagination
@@pagination@@` at scaffold time), and pages until `ToolPage.has_more` is
false. Point `@@short_env@@_URL` and this connector's auth settings (see
`.env.example`) at the real vendor API, then replace `_LIST_PATH` and the
`items`/pagination field names in `@@pkg_dir@@/mcp/mcp_@@domain@@.py` with
the vendor's real endpoint and response shape — keeping
`connector_manifest.yml`'s sync preset in step, or update both together and
rerun `scripts/pin_tool_schema.py`.
"""

PAGES_DEPLOYMENT_MD = """\
# Deployment

Local MCP usage defaults to `stdio`. A networked deployment requires
`AUTH_TYPE` configured and a loopback-only publish behind an operator-owned
authenticated TLS ingress — see `docker/mcp.compose.yml`.

The API client's own credentials (`@@short_env@@_TOKEN_REF` and similar,
depending on `--auth`) and TLS profile are `env://` or `openbao://`
references resolved by `@@pkg_dir@@.api_client` at composition time; the
`@@pkg_dir@@.credentials` module resolves any other reference the same way.
No raw secret value is ever written to configuration, images, or generated
files.
"""

PAGES_CONCEPTS_MD = """\
# Concepts

- **Native content primitives** — `skills/`, `prompts/`, `ontology/` and
  `connector_manifest.yml` are served over MCP (`skill://`, `prompts/list`,
  `ontology://`, `shapes://`, `manifest://connector`); nothing is exported
  through a second channel.
- **Governed sync** — `connector_manifest.yml`'s `sync` preset is pinned by
  `tool_schema_sha256`; `McpToolSourceAdapter.discover()` verifies the live
  tool against that pin before any extraction, so a drifted schema fails
  closed.
- **Credentials by reference** — every credential-shaped setting holds an
  `env://` or `openbao://` reference, resolved at the composition root.
"""

CI_YML = """\
name: CI

# The shared workspace gate suite (complexity, KISS, duplication,
# secret-history, tracked-privacy, root-hygiene, dependency-audit,
# orphan-module-gate) lands via the Knuckles-Team/pipelines shared hook
# repository (RF-ADR-009 section 8, lane SHARED-HOOKS) and repository-manager's
# combined gate runner, not as copied scripts in this workflow.

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  gates:
    name: gates
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e # v6
        with:
          version: '0.11.7'
      - name: Sync the locked environment
        run: uv sync --frozen
      - name: Pin the live tool schema fingerprint
        run: uv run --frozen python scripts/pin_tool_schema.py
      - name: Test suite
        run: uv run --frozen python -m pytest -q
      - name: Lint and format
        run: |
          uvx --from ruff==0.16.0 ruff check @@pkg_dir@@ tests
          uvx --from ruff==0.16.0 ruff format --check @@pkg_dir@@ tests
      - name: Type check
        run: uv run --frozen --with mypy==1.20.2 python -m mypy @@pkg_dir@@
"""

PAGES_YML = """\
name: Pages

# Calls the shared Knuckles-Team/pipelines Pages workflow (RF-ADR-009 section
# 5, lane PAGES-FOUNDATION): the shared Material theme via mkdocs INHERIT:
# (shared_theme_enabled), plus canonical agent-readiness delivery
# (agent_readiness_enabled) — pages/agent-readiness.json validated against
# pages/agent-readiness.schema.json, llms.txt + the readiness/mirror
# manifests cross-checked against the built site, and the offline readiness
# TCK. Pinned to the pipelines commit this repository was proved against
# locally; pipelines must be pushed to that ref before this workflow resolves.

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  pages:
    uses: @@github_org@@/pipelines/.github/workflows/pages_pipeline.yml@@@pipelines_sha@@
    with:
      content_source: pages
      shared_theme_enabled: true
      agent_readiness_enabled: true
"""

# ── Python package templates ─────────────────────────────────────────────────

INIT_PY = '''\
"""@@display_name@@ — an MCP connector on agent-connector-sdk."""

from __future__ import annotations

__version__ = "0.1.0"
'''

CREDENTIALS_PY = '''\
"""Credential resolution for @@display_name@@.

Every credential-shaped setting (``*_TOKEN``, ``*_SECRET``, ``*_PASSWORD``,
``*_API_KEY``, ``*_PRIVATE_KEY``) holds an ``env://`` or ``openbao://``
reference — never a raw value — enforced by
``agent_connector_sdk.config.load_config``. This module resolves those
references at the composition root.
"""

from __future__ import annotations

from agent_connector_sdk.config import setting
from agent_connector_sdk.credentials.openbao import OpenBaoCredentialResolver
from agent_connector_sdk.credentials.references import parse_secret_reference
from agent_connector_sdk.credentials.resolver import (
    CompositeCredentialResolver,
    CredentialResolver,
    EnvironmentCredentialResolver,
)

__all__ = ["build_resolver", "resolve_setting"]


def build_resolver() -> CredentialResolver:
    """A resolver for ``env://`` references, plus ``openbao://`` when configured."""
    resolvers: dict[str, CredentialResolver] = {"env": EnvironmentCredentialResolver()}
    openbao = OpenBaoCredentialResolver.from_settings()
    if openbao is not None:
        resolvers["openbao"] = openbao
    return CompositeCredentialResolver(resolvers)


def resolve_setting(key: str, resolver: CredentialResolver | None = None) -> str | None:
    """Resolve the secret reference named by the ``key`` setting, if configured."""
    raw = setting(key)
    if not raw:
        return None
    return (resolver or build_resolver()).resolve(parse_secret_reference(str(raw)))
'''

# ── API client: one governed HTTP client per connector, built only from
# agent-connector-sdk's http/tls/auth layer (never raw httpx/requests, never
# agent-utilities). ``_auth()`` is the one function that varies by --auth mode;
# everything else in api_client.py is identical across modes.
_AUTH_IMPORTS: dict[str, str] = {
    "bearer": "from agent_connector_sdk.auth.static import bearer_auth",
    "basic": "from agent_connector_sdk.auth.static import basic_auth",
    "api_key": "from agent_connector_sdk.auth.static import api_key_auth",
    "client_credentials": (
        "from agent_connector_sdk.auth.oidc import (\n"
        "    ClientCredentialsConfig,\n"
        "    client_credentials_auth,\n"
        ")"
    ),
    "delegated": (
        "from agent_connector_sdk.auth.delegation import "
        "DelegatedTokenAuth, DelegationSettings"
    ),
}

_AUTH_FUNCTIONS: dict[str, str] = {
    "bearer": '''\
def _auth() -> httpx.Auth:
    """The outbound credentials, resolved from settings."""
    return bearer_auth(setting("@@short_env@@_TOKEN_REF"))
''',
    "basic": '''\
def _auth() -> httpx.Auth:
    """The outbound credentials, resolved from settings."""
    return basic_auth(
        setting("@@short_env@@_USERNAME"), setting("@@short_env@@_PASSWORD_REF")
    )
''',
    "api_key": '''\
def _auth() -> httpx.Auth:
    """The outbound credentials, resolved from settings."""
    return api_key_auth(setting("@@short_env@@_API_KEY_REF"), header="X-Api-Key")
''',
    "client_credentials": '''\
def _auth() -> httpx.Auth:
    """The outbound credentials: an OAuth 2.0 client-credentials token."""
    return client_credentials_auth(ClientCredentialsConfig.from_settings())
''',
    "delegated": '''\
def _auth() -> httpx.Auth:
    """The outbound credentials: a token exchanged for the verified MCP caller."""
    token_client = create_http_client(
        HttpClientOptions(base_url=setting("OIDC_TOKEN_URL"))
    )
    return DelegatedTokenAuth(
        DelegationSettings.from_settings(), http_client=token_client
    )
''',
}

API_CLIENT_PY = '''\
"""@@display_name@@ API client.

The governed HTTP client @@pkg_dir@@'s tools call. Base URL, auth and TLS all
resolve from settings at composition time (agent-connector-sdk
pages/http-clients.md); the client itself never reads the ambient environment.
Failures surface as ``agent_connector_sdk.http.errors.HttpProblemError``.
"""

from __future__ import annotations

import httpx
@@auth_imports@@
from agent_connector_sdk.config import setting
from agent_connector_sdk.http.client import create_async_http_client, create_http_client
from agent_connector_sdk.http.options import HttpClientOptions
from agent_connector_sdk.tls.resolve import resolve_tls_profile

__all__ = ["build_client", "build_client_for"]


@@auth_fn@@


def build_client() -> httpx.AsyncClient:
    """Composition root: settings and secret references resolve here, once."""
    return create_async_http_client(
        HttpClientOptions(
            base_url=setting("@@short_env@@_URL"),
            auth=_auth(),
            tls=resolve_tls_profile("@@pkg_dir@@"),
        )
    )


def build_client_for(base_url: str) -> httpx.Client:
    """A synchronous client for ``base_url``, built like :func:`build_client`.

    Used by agent-connector-sdk's HTTP client conformance kit
    (``agent_connector_sdk.testing.http_clients.run_http_client_suite``), which
    points a synchronous factory at its own scripted local server.
    """
    return create_http_client(HttpClientOptions(base_url=base_url, auth=_auth()))
'''

MCP_SERVER_PY = '''\
"""@@display_name@@ MCP server.

Built entirely from agent-connector-sdk: ``create_mcp_server`` for the
governed server factory, ``register_tool_surface`` for the ``MCP_TOOL_MODE``-
routed tool surface, and ``ConnectorContent`` to serve this package's
``skills/``, ``prompts/``, ``ontology/`` and ``connector_manifest.yml`` as
native MCP primitives (RF-ADR-009 section 2.1).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_connector_sdk.mcp.content import ConnectorContent
from agent_connector_sdk.mcp.server import create_mcp_server
from agent_connector_sdk.mcp.tool_surface import register_tool_surface

from @@pkg_dir@@.mcp import register_@@domain@@_tools

__all__ = ["build_server", "mcp_server"]
__version__ = "0.1.0"

CONNECTOR = "@@package_name@@"
#: The repository root: skills/, prompts/, ontology/ and connector_manifest.yml
#: are its direct children (this file lives at <root>/@@pkg_dir@@/mcp_server.py).
REPO_ROOT = Path(__file__).resolve().parent.parent


def build_server(
    *, command_args: list[str] | None = None
) -> tuple[Any, Any, list[Any]]:
    """Build the connector's MCP server. Returns ``(args, mcp, middlewares)``."""
    args, mcp, middlewares = create_mcp_server(
        CONNECTOR,
        version=__version__,
        instructions="@@description@@",
        command_args=command_args,
        content=ConnectorContent(
            connector=CONNECTOR,
            package_root=REPO_ROOT,
            manifest_path=REPO_ROOT / "connector_manifest.yml",
        ),
    )
    register_tool_surface(mcp, service=CONNECTOR, registrars=[register_@@domain@@_tools])
    for middleware in middlewares:
        mcp.add_middleware(middleware)
    return args, mcp, middlewares


def mcp_server() -> None:
    """Console-script entry point."""
    args, mcp, _ = build_server()
    if args.transport == "stdio":
        mcp.run(transport=args.transport)
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    mcp_server()
'''

MCP_INIT_PY = '''\
"""@@display_name@@'s MCP tool domains."""

from __future__ import annotations

from @@pkg_dir@@.mcp.mcp_@@domain@@ import register_@@domain@@_tools

__all__ = ["register_@@domain@@_tools"]
'''

# Tool bodies keyed by --pagination mode: each calls the governed API client
# and returns a ToolPage, matching the ``preset_pagination(mode, ...)`` fields
# ``_preset_dict`` writes into connector_manifest.yml / mcp_source_presets.json
# (agent-connector-sdk pages/http-clients.md).
_TOOL_BODIES: dict[str, str] = {
    "cursor": '''\
    @mcp.tool()
    async def @@tool_name@@(cursor: str | None = None, ctx=None) -> ToolPage:
        """Read one page of @@package_name@@ @@domain@@ items."""
        await ctx_progress(ctx, 0, 1, message="fetching @@domain@@")
        async with build_client() as client:
            document = await arequest_json(
                client, "GET", _LIST_PATH, params={"cursor": cursor}
            )
        await ctx_progress(ctx, 1, 1)
        # Replace "items"/"next" with the vendor's real response field names.
        return ToolPage.from_cursor(document["items"], document.get("next"))
''',
    "page": '''\
    @mcp.tool()
    async def @@tool_name@@(page: int = 0, ctx=None) -> ToolPage:
        """Read one page of @@package_name@@ @@domain@@ items."""
        await ctx_progress(ctx, 0, 1, message="fetching @@domain@@")
        async with build_client() as client:
            document = await arequest_json(
                client,
                "GET",
                _LIST_PATH,
                params={"page": page, "page_size": @@page_size@@},
            )
        await ctx_progress(ctx, 1, 1)
        # Replace "items" with the vendor's real response field name.
        return ToolPage.from_window(document["items"], page_size=@@page_size@@)
''',
    "offset": '''\
    @mcp.tool()
    async def @@tool_name@@(offset: int = 0, ctx=None) -> ToolPage:
        """Read one page of @@package_name@@ @@domain@@ items."""
        await ctx_progress(ctx, 0, 1, message="fetching @@domain@@")
        async with build_client() as client:
            document = await arequest_json(
                client,
                "GET",
                _LIST_PATH,
                params={"offset": offset, "limit": @@page_size@@},
            )
        await ctx_progress(ctx, 1, 1)
        # Replace "items" with the vendor's real response field name.
        return ToolPage.from_window(document["items"], page_size=@@page_size@@)
''',
}

#: Just the parameter the tool takes besides ``ctx`` — reused by the test
#: suite's malformed server, which must declare the identical input schema.
TOOL_SIGNATURES: dict[str, str] = {
    "cursor": "cursor: str | None = None",
    "page": "page: int = 0",
    "offset": "offset: int = 0",
}

MCP_DOMAIN_PY = '''\
"""@@display_name@@ — the ``@@tool_name@@`` MCP tool.

Calls the governed API client from ``@@pkg_dir@@.api_client`` and returns one
``agent_connector_sdk.http.pagination.ToolPage`` per call. ``build_client()``
is called per request, not at import/registration time, so listing tools or
pinning the schema needs no credentials configured; hoist it to a longer-lived
client for connection reuse once this is real production traffic. The
matching ``connectors/mcp_source_presets.json`` entry is built by
``preset_pagination("@@pagination@@", ...)`` (agent-connector-sdk
pages/http-clients.md), so extraction pages through exactly what this tool
returns. Replace ``_LIST_PATH`` and the ``items``/pagination field names with
the vendor's real endpoint and response shape.
"""

from __future__ import annotations

from agent_connector_sdk.http.pagination import ToolPage
from agent_connector_sdk.http.responses import arequest_json
from agent_connector_sdk.progress import ctx_progress
from fastmcp import FastMCP

from @@pkg_dir@@.api_client import build_client

__all__ = ["register_@@domain@@_tools"]

_LIST_PATH = "@@list_path@@"


def register_@@domain@@_tools(mcp: FastMCP) -> None:
    """Register the ``@@tool_name@@`` tool."""

@@tool_body@@'''

PIN_TOOL_SCHEMA_PY = '''\
#!/usr/bin/env python3
"""Pin ``@@tool_name@@``'s live MCP schema fingerprint.

Run once after ``uv sync`` (once agent-connector-sdk and fastmcp are
installed) and again whenever the tool's parameters change. Writes the
compatibility fingerprint into both ``connector_manifest.yml``'s ``sync[0]``
entry and ``connectors/tool_schema_fingerprints.json`` so
``McpToolSourceAdapter.discover()`` can verify the live tool without drift
instead of failing closed on a stale placeholder.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import yaml
from agent_connector_sdk.manifest.tool_schema import (
    canonical_input_schema,
    compatibility_fingerprint,
)
from fastmcp import Client

from @@pkg_dir@@.mcp_server import build_server

ROOT = Path(__file__).resolve().parent.parent
TOOL_NAME = "@@tool_name@@"
MANIFEST_PATH = ROOT / "connector_manifest.yml"
FINGERPRINTS_PATH = ROOT / "connectors" / "tool_schema_fingerprints.json"


async def _live_schema() -> dict[str, object]:
    _, mcp, _ = build_server(command_args=[])
    async with Client(mcp) as client:
        tools = await client.list_tools()
    matches = [tool for tool in tools if tool.name == TOOL_NAME]
    if len(matches) != 1:
        raise SystemExit(
            f"expected exactly one tool named {TOOL_NAME!r}, found {len(matches)}"
        )
    return canonical_input_schema(matches[0], include_presentation=False)


def _write_manifest(digest: str) -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    updated = False
    for entry in manifest.get("sync", []):
        if entry.get("tool") == TOOL_NAME:
            entry["tool_schema_sha256"] = digest
            entry.setdefault("raw", {})["tool_schema_sha256"] = digest
            updated = True
    if not updated:
        raise SystemExit(f"no sync entry in {MANIFEST_PATH} names tool {TOOL_NAME!r}")
    MANIFEST_PATH.write_text(
        yaml.safe_dump(manifest, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )


def _write_fingerprints(digest: str) -> None:
    document = json.loads(FINGERPRINTS_PATH.read_text(encoding="utf-8"))
    document["tools"][TOOL_NAME] = digest
    FINGERPRINTS_PATH.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\\n", encoding="utf-8"
    )


def main() -> None:
    digest = compatibility_fingerprint(TOOL_NAME, asyncio.run(_live_schema()))
    _write_manifest(digest)
    _write_fingerprints(digest)
    print(f"Pinned {TOOL_NAME} -> {digest}")


if __name__ == "__main__":
    main()
'''

# ── Content: skills / prompts / ontology ─────────────────────────────────────

SKILL_MD = """\
---
name: @@package_name@@-@@domain@@
description: Read the @@package_name@@ stream one page at a time through the @@package_name@@ MCP server.
license: MIT
---
# @@display_name@@ @@domain@@

Call `@@tool_name@@` with `@@pagination@@` (the connector's pagination
parameter). It calls the real @@package_name@@ API and returns a page of
items; keep calling with the next `@@pagination@@` value until the result's
`has_more` is false.
"""

PROMPT_CORE_DIRECTIVE = (
    "You operate the @@package_name@@ stream through the @@tool_name@@ tool, "
    "which calls the real @@package_name@@ API. Page through it with "
    "@@pagination@@ and stop when the result's has_more is false."
)

PROMPT_JSON_TEMPLATE: dict[str, str] = {
    "task": "@@package_name@@",
    "type": "prompt",
    "description": "Operates the @@package_name@@ stream.",
    "schema_version": "1.0",
    "source": "@@package_name@@",
}

ONTOLOGY_TTL = """\
@prefix @@pkg_dir@@: <https://knuckles-team.github.io/@@package_name@@/ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

@@pkg_dir@@:@@resource_name@@ a owl:Class .
"""

SHAPES_TTL = """\
@prefix @@pkg_dir@@: <https://knuckles-team.github.io/@@package_name@@/ontology#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .

@@pkg_dir@@:@@resource_name@@Shape
  a sh:NodeShape ;
  sh:targetClass @@pkg_dir@@:@@resource_name@@ ;
  sh:property [
    sh:path @@pkg_dir@@:id ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
  ] .
"""

# ── Tests ─────────────────────────────────────────────────────────────────────

TESTS_SERVERS_PY = '''\
"""In-process servers used by the test suite: the real connector server, and a
malformed variant for the conformance kit's rejection check."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from @@pkg_dir@@.mcp_server import build_server

TOOL_NAME = "@@tool_name@@"


def build_well_formed_server() -> Any:
    """The connector's real MCP server."""
    _, mcp, _ = build_server(command_args=[])
    return mcp


def build_malformed_server() -> Any:
    """Same input schema as the real tool (so its pinned fingerprint still
    matches); the payload is not a record list."""
    mcp: FastMCP[Any] = FastMCP("@@package_name@@", version="0.1.0")

    @mcp.tool()
    def @@tool_name@@(@@malformed_signature@@, ctx=None) -> dict[str, Any]:
        """Read the @@package_name@@ @@domain@@ stream one page at a time."""
        return {"items": "not-a-list", "next_cursor": None, "has_more": False}

    return mcp
'''

TESTS_CONFTEST_PY = '''\
"""Shared fixtures: in-process sessions and the manifest-driven source adapter.

``sessions`` points the real connector server's tool at a local
``ScriptedHttpServer`` (the same double ``tests/test_api_client.py`` uses)
instead of a real vendor target, pre-loaded with enough scripted pages to
cover every check ``run_source_adapter_suite`` runs against it (an initial
sweep, pagination, checkpoint-resume and idempotent-rerun each sweep again).
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from contextlib import AbstractAsyncContextManager
from pathlib import Path

import pytest
from agent_connector_sdk.adapters.mcp_tool import McpToolSourceAdapter
from agent_connector_sdk.manifest.loader import require_valid_connector_package
from agent_connector_sdk.ports.session import McpSession, TransportEndpoint
from agent_connector_sdk.testing.http_server import ScriptedHttpServer, ScriptedResponse
from agent_connector_sdk.testing.results import SessionFactory
from agent_connector_sdk.transports.mcp import McpTransport
from servers import build_malformed_server, build_well_formed_server

CONNECTOR = "@@package_name@@"
REPO_ROOT = Path(__file__).resolve().parent.parent


def _factory(build: Callable[[], object]) -> SessionFactory:
    def open_session() -> AbstractAsyncContextManager[McpSession]:
        return McpTransport().session(TransportEndpoint(in_process=build()))

    return open_session


def _paged_items(start: int, count: int) -> list[dict[str, str]]:
    return [
        {"id": str(start + i), "title": f"Item {start + i}", "text": "Body"}
        for i in range(count)
    ]


@@scripted_responses@@

def _set_auth_env(monkeypatch: pytest.MonkeyPatch, base_url: str) -> None:
@@auth_env_setup@@


@pytest.fixture
def sessions(monkeypatch: pytest.MonkeyPatch) -> Iterator[SessionFactory]:
    """Fresh sessions to the real connector server, its tool pointed at a
    local ``ScriptedHttpServer`` standing in for the vendor API."""
    with ScriptedHttpServer(*_scripted_responses()) as server:
        _set_auth_env(monkeypatch, server.base_url)
        yield _factory(build_well_formed_server)


@pytest.fixture
def malformed_sessions() -> SessionFactory:
    """Fresh sessions to a connector whose records are malformed."""
    return _factory(build_malformed_server)


@pytest.fixture
def repo_root() -> Path:
    """The connector package's repository root."""
    return REPO_ROOT


@pytest.fixture
def adapter() -> McpToolSourceAdapter:
    """The ``mcp_tool`` adapter built from the manifest's sync entry."""
    manifest = require_valid_connector_package(REPO_ROOT)
    return McpToolSourceAdapter.from_sync_spec(manifest.sync[0], connector=CONNECTOR)
'''

#: Two deterministic, byte-identical-on-every-cycle pages, one per
#: ``ctx["pagination"]`` mode, matching ``ToolPage``'s exact wire shape
#: (``agent_connector_sdk.http.pagination.preset_pagination``).
_CONFORMANCE_PAGE_BODIES: dict[str, str] = {
    "cursor": '''\
def _page_bodies() -> list[bytes]:
    return [
        json.dumps({"items": _paged_items(1, 1), "next": "page-2"}).encode(),
        json.dumps({"items": _paged_items(2, 1), "next": None}).encode(),
    ]
''',
    "page": '''\
def _page_bodies() -> list[bytes]:
    return [
        json.dumps({"items": _paged_items(1, @@page_size@@)}).encode(),
        json.dumps({"items": _paged_items(1 + @@page_size@@, 1)}).encode(),
    ]
''',
}
_CONFORMANCE_PAGE_BODIES["offset"] = _CONFORMANCE_PAGE_BODIES["page"]

#: Static auth (bearer/basic/api_key): one HTTP request per page. OAuth
#: (client_credentials/delegated, ``_OAUTH_AUTH_MODES``): a token response
#: ahead of every page request, mirroring ``TESTS_API_CLIENT_OAUTH_PY``.
_CONFORMANCE_RESPONSES_STATIC = '''\
def _scripted_responses() -> list[ScriptedResponse]:
    return [ScriptedResponse(body=body) for body in _page_bodies() * 8]
'''

_CONFORMANCE_RESPONSES_OAUTH = '''\
_TOKEN_BODY = json.dumps(
    {"access_token": "minted-token", "token_type": "bearer", "expires_in": 3600}
).encode()


def _scripted_responses() -> list[ScriptedResponse]:
    responses: list[ScriptedResponse] = []
    for body in _page_bodies() * 8:
        responses.append(ScriptedResponse(body=_TOKEN_BODY))
        responses.append(ScriptedResponse(body=body))
    return responses
'''

TESTS_MANIFEST_PY = '''\
"""``connector_manifest.yml`` agrees with its presets and pinned fingerprints."""

from __future__ import annotations

from pathlib import Path

from agent_connector_sdk.manifest.loader import require_valid_connector_package

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_manifest_matches_presets_and_fingerprints() -> None:
    manifest = require_valid_connector_package(REPO_ROOT)
    assert manifest.connector == "@@package_name@@"
    assert manifest.sync[0].tool == "@@tool_name@@"
    assert manifest.sync[0].preset == "@@domain@@"
'''

TESTS_MCP_SERVER_PY = '''\
"""The MCP server lists its tools, skills, prompts and content resources.

The ``@@tool_name@@`` tool itself calls a real vendor API, so a live end-to-end
call belongs to ``tests/test_api_client.py`` (a scripted local server), not
here.
"""

from __future__ import annotations

from fastmcp import Client

from @@pkg_dir@@.mcp_server import build_server


async def test_server_serves_tools_skills_prompts_and_resources() -> None:
    _, mcp, _ = build_server(command_args=[])
    async with Client(mcp) as client:
        tools = {tool.name for tool in await client.list_tools()}
        prompts = {prompt.name for prompt in await client.list_prompts()}
        resources = {str(resource.uri) for resource in await client.list_resources()}

        assert "@@tool_name@@" in tools
        assert "@@package_name@@" in prompts
        assert "ontology://@@package_name@@/@@package_name@@.ttl" in resources
        assert "shapes://@@package_name@@/@@package_name@@.shapes.ttl" in resources
        assert "manifest://connector" in resources

        skill_text = "".join(
            block.text
            for block in await client.read_resource(
                "skill://@@package_name@@-@@domain@@/SKILL.md"
            )
        )
        assert "@@tool_name@@" in skill_text
'''

TESTS_CREDENTIALS_PY = '''\
"""Secret reference parsing and resolution."""

from __future__ import annotations

import pytest
from agent_connector_sdk.credentials.references import SecretReferenceError
from agent_connector_sdk.credentials.resolver import CredentialUnavailableError

from @@pkg_dir@@.credentials import build_resolver, resolve_setting


def test_env_reference_resolves(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("@@short_env@@_TOKEN", "s3cr3t")
    monkeypatch.setenv("@@short_env@@_TOKEN_REF", "env://@@short_env@@_TOKEN")
    assert resolve_setting("@@short_env@@_TOKEN_REF") == "s3cr3t"


def test_unset_reference_is_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("@@short_env@@_TOKEN_REF", raising=False)
    assert resolve_setting("@@short_env@@_TOKEN_REF") is None


def test_malformed_reference_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("@@short_env@@_TOKEN_REF", "not-a-reference")
    with pytest.raises(SecretReferenceError):
        resolve_setting("@@short_env@@_TOKEN_REF")


def test_missing_env_target_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("@@short_env@@_MISSING", raising=False)
    monkeypatch.setenv("@@short_env@@_TOKEN_REF", "env://@@short_env@@_MISSING")
    with pytest.raises(CredentialUnavailableError):
        resolve_setting("@@short_env@@_TOKEN_REF", build_resolver())
'''

TESTS_CONFORMANCE_PY = '''\
"""The manifest's sync preset passes agent-connector-sdk's conformance kit.

Runs by default, no marker: ``sessions`` (see ``conftest.py``) builds the
real MCP server, but its tool's calls through ``@@pkg_dir@@.api_client``
resolve against a local ``ScriptedHttpServer`` instead of a real vendor
target — the same double ``tests/test_api_client.py``'s proof uses.
``malformed_sessions`` never leaves the process at all.
"""

from __future__ import annotations

from agent_connector_sdk.adapters.mcp_tool import McpToolSourceAdapter
from agent_connector_sdk.testing.results import SessionFactory, assert_conformant
from agent_connector_sdk.testing.source_adapters import run_source_adapter_suite


async def test_sync_preset_passes_the_conformance_kit(
    adapter: McpToolSourceAdapter,
    sessions: SessionFactory,
    malformed_sessions: SessionFactory,
) -> None:
    results = await run_source_adapter_suite(adapter, sessions, malformed_sessions)
    assert_conformant(results)
'''

# ── tests/test_api_client.py: proves the governed API client, not just the
# manifest's sync preset. Two shapes: STATIC (bearer/basic/api_key) whose
# factory needs only a base URL, so it also runs the SDK's
# run_http_client_suite; OAUTH (client_credentials/delegated) whose auth
# mints a token from a separately configured endpoint, so the generic kit
# (which assumes a self-contained factory) does not apply — see the
# generated module's own docstring.
_OAUTH_AUTH_MODES = frozenset({"client_credentials", "delegated"})

_AUTH_ENV_SETUP: dict[str, str] = {
    "bearer": '''\
    monkeypatch.setenv("@@short_env@@_URL", base_url)
    monkeypatch.setenv("@@short_env@@_TOKEN", "test-token")
    monkeypatch.setenv("@@short_env@@_TOKEN_REF", "env://@@short_env@@_TOKEN")
''',
    "basic": '''\
    monkeypatch.setenv("@@short_env@@_URL", base_url)
    monkeypatch.setenv("@@short_env@@_USERNAME", "test-user")
    monkeypatch.setenv("@@short_env@@_PASSWORD", "test-pass")
    monkeypatch.setenv("@@short_env@@_PASSWORD_REF", "env://@@short_env@@_PASSWORD")
''',
    "api_key": '''\
    monkeypatch.setenv("@@short_env@@_URL", base_url)
    monkeypatch.setenv("@@short_env@@_API_KEY", "test-key")
    monkeypatch.setenv("@@short_env@@_API_KEY_REF", "env://@@short_env@@_API_KEY")
''',
    "client_credentials": '''\
    monkeypatch.setenv("@@short_env@@_URL", base_url)
    monkeypatch.setenv("OIDC_TOKEN_URL", base_url)
    monkeypatch.setenv("OIDC_CLIENT_ID", "test-client")
    monkeypatch.setenv("OIDC_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("OIDC_CLIENT_SECRET_REF", "env://OIDC_CLIENT_SECRET")
    monkeypatch.setenv("OIDC_AUDIENCE", "@@package_name@@-api")
''',
    "delegated": '''\
    monkeypatch.setenv("@@short_env@@_URL", base_url)
    monkeypatch.setenv("ENABLE_DELEGATION", "true")
    monkeypatch.setenv("OIDC_TOKEN_URL", base_url)
    monkeypatch.setenv("OIDC_CLIENT_ID", "test-client")
    monkeypatch.setenv("OIDC_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("OIDC_CLIENT_SECRET_REF", "env://OIDC_CLIENT_SECRET")
    monkeypatch.setenv("AUDIENCE", "@@package_name@@-api")
    monkeypatch.setattr(
        "agent_connector_sdk.auth.delegation.get_access_token",
        lambda: type("_FakeToken", (), {"token": "caller-token"})(),
    )
''',
}

_AUTH_HEADER_ASSERT: dict[str, str] = {
    "bearer": 'assert business.headers.get("authorization") == "Bearer test-token"',
    "basic": 'assert business.headers.get("authorization", "").startswith("Basic ")',
    "api_key": 'assert business.headers.get("x-api-key") == "test-key"',
    "client_credentials": (
        'assert business.headers.get("authorization") == "Bearer minted-token"'
    ),
    "delegated": (
        'assert business.headers.get("authorization") == "Bearer minted-token"'
    ),
}

TESTS_API_CLIENT_STATIC_PY = '''\
"""The governed API client: conformance kit + one real tool call end to end."""

from __future__ import annotations

import json

import pytest
from agent_connector_sdk.http.errors import HttpProblemError
from agent_connector_sdk.http.problems import PROBLEM_JSON
from agent_connector_sdk.http.responses import request_json
from agent_connector_sdk.testing.http_clients import run_http_client_suite
from agent_connector_sdk.testing.http_server import ScriptedHttpServer, ScriptedResponse
from agent_connector_sdk.testing.results import assert_conformant
from fastmcp import Client

from @@pkg_dir@@.api_client import build_client_for
from @@pkg_dir@@.mcp_server import build_server

_OK_BODY = b\'{"items": [{"id": "1", "title": "One", "text": "Body"}]}\'
_PROBLEM_BODY = b\'{"type": "https://api.example.invalid/missing", "title": "Missing"}\'


def _set_auth_env(monkeypatch: pytest.MonkeyPatch, base_url: str) -> None:
@@auth_env_setup@@


def test_client_factory_passes_the_conformance_kit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_auth_env(monkeypatch, "https://api.example.invalid")
    assert_conformant(run_http_client_suite(build_client_for))


async def test_tool_calls_the_client_end_to_end(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with ScriptedHttpServer(ScriptedResponse(body=_OK_BODY)) as server:
        _set_auth_env(monkeypatch, server.base_url)
        _, mcp, _ = build_server(command_args=[])
        async with Client(mcp) as client:
            result = await client.call_tool("@@tool_name@@", {})
        business = server.requests[0]
        @@auth_header_assert@@
        payload = json.loads(result.content[0].text)
        assert payload["items"] == [{"id": "1", "title": "One", "text": "Body"}]


def test_problem_response_maps_to_http_problem_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with ScriptedHttpServer(
        ScriptedResponse(
            status=404, body=_PROBLEM_BODY, headers={"Content-Type": PROBLEM_JSON}
        )
    ) as server:
        _set_auth_env(monkeypatch, server.base_url)
        with (
            build_client_for(server.base_url) as client,
            pytest.raises(HttpProblemError) as excinfo,
        ):
            request_json(client, "GET", "/@@domain@@")
        assert excinfo.value.problem.status == 404
'''

TESTS_API_CLIENT_OAUTH_PY = '''\
"""The governed API client: one real tool call end to end, token mint included.

``run_http_client_suite`` is not run here: it assumes a factory that is fully
self-contained given only a base URL, but this connector's OAuth 2.0 auth
mints its token from a separately configured endpoint (``OIDC_TOKEN_URL``) —
here pointed at the same scripted server as the business call, ahead of it in
the response queue, so both requests resolve against one local server.
"""

from __future__ import annotations

import json

import pytest
from agent_connector_sdk.http.errors import HttpProblemError
from agent_connector_sdk.http.problems import PROBLEM_JSON
from agent_connector_sdk.http.responses import request_json
from agent_connector_sdk.testing.http_server import ScriptedHttpServer, ScriptedResponse
from fastmcp import Client

from @@pkg_dir@@.api_client import build_client_for
from @@pkg_dir@@.mcp_server import build_server

_TOKEN_BODY = (
    b\'{"access_token": "minted-token", "token_type": "bearer", "expires_in": 3600}\'
)
_OK_BODY = b\'{"items": [{"id": "1", "title": "One", "text": "Body"}]}\'
_PROBLEM_BODY = b\'{"type": "https://api.example.invalid/missing", "title": "Missing"}\'


def _set_auth_env(monkeypatch: pytest.MonkeyPatch, base_url: str) -> None:
@@auth_env_setup@@


async def test_tool_calls_the_client_end_to_end(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with ScriptedHttpServer(
        ScriptedResponse(body=_TOKEN_BODY), ScriptedResponse(body=_OK_BODY)
    ) as server:
        _set_auth_env(monkeypatch, server.base_url)
        _, mcp, _ = build_server(command_args=[])
        async with Client(mcp) as client:
            result = await client.call_tool("@@tool_name@@", {})
        business = server.requests[1]
        @@auth_header_assert@@
        payload = json.loads(result.content[0].text)
        assert payload["items"] == [{"id": "1", "title": "One", "text": "Body"}]


def test_problem_response_maps_to_http_problem_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with ScriptedHttpServer(
        ScriptedResponse(body=_TOKEN_BODY),
        ScriptedResponse(
            status=404, body=_PROBLEM_BODY, headers={"Content-Type": PROBLEM_JSON}
        ),
    ) as server:
        _set_auth_env(monkeypatch, server.base_url)
        with (
            build_client_for(server.base_url) as client,
            pytest.raises(HttpProblemError) as excinfo,
        ):
            request_json(client, "GET", "/@@domain@@")
        assert excinfo.value.problem.status == 404
'''

# ── Manifest / structured data ───────────────────────────────────────────────


def _connector_manifest(
    ctx: dict[str, str], preset: dict[str, object]
) -> dict[str, object]:
    resource = ctx["resource_name"]
    return {
        "connector": ctx["package_name"],
        "ontology_source": ctx["package_name"],
        "schema_version": "1",
        "resources": [
            {
                "name": resource,
                "label": ctx["display_name"] + " Item",
                "id_prefix": ctx["pkg_dir"],
                "relations": [],
            }
        ],
        "actions": [
            {
                "id": f"read_{ctx['doc_type']}",
                "name": f"Read {ctx['display_name']} Stream",
                "description": f"Page through the {ctx['package_name']} stream.",
            }
        ],
        "identity": {
            "id_field": {ctx["doc_type"]: "id"},
            "title_field": {ctx["doc_type"]: "title"},
            "text_field": {ctx["doc_type"]: "text"},
        },
        "schema_mappings": {
            resource: {"ontology_class": "Document", "fields": {}},
        },
        "sync": [
            {
                "preset": ctx["domain"],
                "server": preset["server"],
                "tool": preset["tool"],
                "action": preset["action"],
                "records_path": preset["records_path"],
                "id_field": preset["id_field"],
                "title_field": preset["title_field"],
                "text_field": preset["text_field"],
                "updated_field": preset.get("updated_field"),
                "pagination": preset["pagination"],
                "doc_type": preset["doc_type"],
                "tool_schema_sha256": "PENDING-RUN-scripts/pin_tool_schema.py",
                "raw": {
                    **preset,
                    "tool_schema_sha256": "PENDING-RUN-scripts/pin_tool_schema.py",
                },
            }
        ],
        "provenance": {
            "generated_by": "agent-package-builder/scaffold_package.py",
            "source_artifacts": [
                "connectors/mcp_source_presets.json",
                "connectors/tool_schema_fingerprints.json",
                f"ontology/{ctx['package_name']}.ttl",
            ],
            "integrity": {
                "algorithm": "urdna2015-sha256",
                "hash": "0" * 64,
                "triple_count": 1,
            },
        },
        "review_todos": [
            f"Point {ctx['short_env']}_URL and this connector's auth settings "
            "at the real vendor API, and replace _LIST_PATH and the "
            "items/pagination field names in "
            f"{ctx['pkg_dir']}/mcp/mcp_{ctx['domain']}.py with the vendor's "
            "real endpoint and response shape.",
            "Run scripts/pin_tool_schema.py after uv sync and whenever the "
            "tool's parameters change.",
            "Map real ontology classes/fields in schema_mappings and recompute "
            "the provenance integrity hash from the real ontology graph.",
        ],
    }


def _tool_schema_fingerprints(ctx: dict[str, str]) -> dict[str, object]:
    return {
        "algorithm": "agent-utilities:mcp-tool-schema-compat:v1",
        "connector": ctx["package_name"],
        "schema_version": "1",
        "tools": {ctx["tool_name"]: "PENDING-RUN-scripts/pin_tool_schema.py"},
    }


def _mcp_config(ctx: dict[str, str]) -> dict[str, object]:
    return {
        "mcpServers": {
            ctx["package_name"]: {
                "command": ctx["mcp_cmd"],
                "args": [],
                "env": {"MCP_TOOL_MODE": "intent"},
            }
        }
    }


def _agent_readiness_input(ctx: dict[str, str]) -> dict[str, object]:
    """The applicability declaration ``pages/agent-readiness.json`` carries.

    Validated at Pages-build time by both the universal-skills generator
    (``agent_readiness._validate_input``, delegated to by
    ``repository_manager.docs_readiness``) and the pipelines readiness TCK
    (``pages_readiness._validate_readiness_input``). ``mcp``/``api``/``a2a``
    are declared inapplicable: the pipelines TCK requires a public HTTPS
    ``endpoint`` for any applicable ``mcp``/``a2a`` capability, and this
    connector's default transport is stdio with no such endpoint to prove.
    ``skills`` is declared inapplicable too, even though this package ships
    real skills: the universal-skills generator adds
    ``.well-known/agent-skills.json`` to its "generated" output list whenever
    ``skills.applicable`` and ``applicability.discoverability`` are both
    true, but the pipelines TCK's own output allowlist does not accept a
    ``.well-known/*`` path — declaring ``skills.applicable: true`` here would
    make the two canonical validators disagree. ``discoverability`` itself
    must stay true: the pipelines TCK's Markdown-mirror check requires it (an
    inapplicable mirror carries no page URLs to validate). See
    ``pages/deployment.md`` and ``AGENTS.md`` for the operator path once a
    real networked endpoint exists.
    """
    return {
        "schema_version": "agent-readiness/v1",
        "project": {"name": ctx["package_name"], "kind": "package"},
        "applicability": {
            "content": True,
            "discoverability": True,
            "access_policy": True,
            "capabilities": True,
            "errors": False,
            "provenance": False,
            "measurement": False,
            "deployment": True,
        },
        "standards": [{"id": "RFC 8259", "kind": "rfc", "level": "normative"}],
        "content_signals": {"policy": "unset"},
        "budgets": {"curated_chars": 8000, "summary_chars": 600, "full_chars": 0},
        "capabilities": {
            "api": {"applicable": False},
            "mcp": {"applicable": False},
            "a2a": {"applicable": False},
            "skills": {"applicable": False},
        },
    }


GENERATE_AGENT_READINESS_PY = '''\
#!/usr/bin/env python3
"""Regenerate ``llms.txt`` and the readiness/mirror manifests.

Delegates to universal-skills' canonical agent-readiness builder (the same
authority ``repository_manager.docs_readiness`` resolves via
``importlib.resources``) so this package never carries its own copy of that
~1,400-line generator. Requires the ``docs`` dependency group
(``uv sync --group docs``). Run after editing ``pages/*.md`` or
``pages/agent-readiness.json``, before a Pages build.
"""

from __future__ import annotations

import importlib.resources
import importlib.util
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def _find(root: Any, filename: str) -> Any | None:
    for child in root.iterdir():
        if child.name == filename:
            return child
        if child.is_dir():
            found = _find(child, filename)
            if found is not None:
                return found
    return None


def _generator() -> Any:
    package = importlib.resources.files("universal_skills")
    candidate = _find(package, "agent_readiness.py")
    if candidate is None:
        raise SystemExit(
            "universal-skills' agent_readiness.py was not found; run "
            "`uv sync --group docs` first."
        )
    with importlib.resources.as_file(candidate) as script_path:
        spec = importlib.util.spec_from_file_location(
            "_agent_readiness_generator", script_path
        )
        if spec is None or spec.loader is None:
            raise SystemExit("agent_readiness.py could not be loaded")
        module = importlib.util.module_from_spec(spec)
        # dataclasses' own machinery resolves a class's module by name through
        # sys.modules, so the module must be registered before exec_module
        # runs its @dataclass-decorated class bodies (the same registration
        # repository_manager.docs_readiness._load_generator_authority does).
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    return module.generate


def main() -> None:
    generate = _generator()
    result = generate(
        ROOT,
        applicability=ROOT / "pages" / "agent-readiness.json",
        check=False,
        adopt_existing=True,
    )
    generated = ", ".join(result["generated"])
    print(f"Generated: {generated}")


if __name__ == "__main__":
    main()
'''

# ── Orchestration ─────────────────────────────────────────────────────────────


def _env_example_source(ctx: dict[str, str]) -> str:
    client_env_block = render(_CLIENT_ENV_BLOCKS[ctx["auth_mode"]], **ctx)
    return render(ENV_EXAMPLE, client_env_block=client_env_block, **ctx)


def _write_root_files(root: Path, ctx: dict[str, str]) -> None:
    for path, template in (
        ("pyproject.toml", PYPROJECT_TOML),
        (".bumpversion.cfg", BUMPVERSION_CFG),
        (".pre-commit-config.yaml", PRECOMMIT_CONFIG),
        ("pytest.ini", PYTEST_INI),
        (".codespellignore", CODESPELLIGNORE),
        ("CLAUDE.md", CLAUDE_MD),
        ("LICENSE", LICENSE_MIT),
        ("CHANGELOG.md", CHANGELOG_MD),
        ("MANIFEST.in", MANIFEST_IN),
        (".gitignore", GITIGNORE),
        (".gitattributes", GITATTRIBUTES),
        (".dockerignore", DOCKERIGNORE),
        ("AGENTS.md", ROOT_AGENTS_MD),
        ("README.md", README_MD),
        ("mkdocs.yml", MKDOCS_YML),
    ):
        _write_generated_text(root / path, render(template, **ctx))
    _write_generated_text(root / ".env.example", _env_example_source(ctx))

    _write_generated_text(root / "docker" / "Dockerfile", render(DOCKERFILE, **ctx))
    _write_generated_text(
        root / "docker" / "debug.Dockerfile", render(DEBUG_DOCKERFILE, **ctx)
    )
    _write_generated_text(
        root / "docker" / "mcp.compose.yml", render(MCP_COMPOSE_YML, **ctx)
    )
    _write_generated_text(
        root / ".github" / "workflows" / "ci.yml", render(CI_YML, **ctx)
    )
    _write_generated_text(
        root / ".github" / "workflows" / "pages.yml", render(PAGES_YML, **ctx)
    )

    for name, template in (
        ("index.md", PAGES_INDEX_MD),
        ("installation.md", PAGES_INSTALLATION_MD),
        ("usage.md", PAGES_USAGE_MD),
        ("deployment.md", PAGES_DEPLOYMENT_MD),
        ("concepts.md", PAGES_CONCEPTS_MD),
    ):
        _write_generated_text(root / "pages" / name, render(template, **ctx))

    _write_generated_json(
        root / "pages" / "agent-readiness.json", _agent_readiness_input(ctx)
    )
    _write_generated_text(
        root / "pages" / "agent-readiness.schema.json",
        (Path(__file__).resolve().parent / "agent_readiness_schema.json").read_text(
            encoding="utf-8"
        ),
    )
    _write_generated_text(
        root / "scripts" / "generate_agent_readiness.py",
        render(GENERATE_AGENT_READINESS_PY, **ctx),
    )


def _api_client_source(ctx: dict[str, str]) -> str:
    """Render ``api_client.py`` for ``ctx["auth_mode"]``."""
    auth_fn = render(_AUTH_FUNCTIONS[ctx["auth_mode"]], **ctx).rstrip("\n")
    values = {**ctx, "auth_imports": _AUTH_IMPORTS[ctx["auth_mode"]], "auth_fn": auth_fn}
    return render(API_CLIENT_PY, **values)


def _mcp_domain_source(ctx: dict[str, str]) -> str:
    """Render ``mcp/mcp_<domain>.py`` for ``ctx["pagination"]``."""
    tool_body = render(_TOOL_BODIES[ctx["pagination"]], **ctx)
    return render(MCP_DOMAIN_PY, tool_body=tool_body, **ctx)


def _write_package(root: Path, ctx: dict[str, str]) -> None:
    pkg = root / ctx["pkg_dir"]
    _write_generated_text(pkg / "__init__.py", render(INIT_PY, **ctx))
    _write_generated_text(pkg / "py.typed", "")
    _write_generated_text(pkg / "credentials.py", render(CREDENTIALS_PY, **ctx))
    _write_generated_text(pkg / "api_client.py", _api_client_source(ctx))
    _write_generated_text(pkg / "mcp_server.py", render(MCP_SERVER_PY, **ctx))
    _write_generated_text(pkg / "mcp" / "__init__.py", render(MCP_INIT_PY, **ctx))
    _write_generated_text(
        pkg / "mcp" / f"mcp_{ctx['domain']}.py", _mcp_domain_source(ctx)
    )
    _write_generated_text(
        root / "scripts" / "pin_tool_schema.py", render(PIN_TOOL_SCHEMA_PY, **ctx)
    )


def _write_content(root: Path, ctx: dict[str, str]) -> None:
    skill_dir = f"{ctx['package_name']}-{ctx['domain']}"
    _write_generated_text(
        root / "skills" / skill_dir / "SKILL.md", render(SKILL_MD, **ctx)
    )
    prompt: dict[str, object] = {
        key: render(value, **ctx) for key, value in PROMPT_JSON_TEMPLATE.items()
    }
    prompt["instructions"] = {"core_directive": render(PROMPT_CORE_DIRECTIVE, **ctx)}
    _write_generated_json(root / "prompts" / f"{ctx['package_name']}.json", prompt)
    _write_generated_text(
        root / "ontology" / f"{ctx['package_name']}.ttl", render(ONTOLOGY_TTL, **ctx)
    )
    _write_generated_text(
        root / "ontology" / "shapes" / f"{ctx['package_name']}.shapes.ttl",
        render(SHAPES_TTL, **ctx),
    )

    preset = _preset_dict(ctx)
    _write_generated_json(
        root / "connectors" / "mcp_source_presets.json",
        {"_comment": f"Sync preset for {ctx['package_name']}.", ctx["domain"]: preset},
    )
    _write_generated_json(
        root / "connectors" / "tool_schema_fingerprints.json",
        _tool_schema_fingerprints(ctx),
    )
    _write_yaml_manifest(root, ctx, preset)
    _write_generated_json(root / "mcp_config.json", _mcp_config(ctx))


def _write_yaml_manifest(
    root: Path, ctx: dict[str, str], preset: dict[str, object]
) -> None:
    manifest = _connector_manifest(ctx, preset)
    text = yaml.safe_dump(manifest, sort_keys=False, default_flow_style=False)
    _write_generated_text(root / "connector_manifest.yml", text)


def _test_servers_source(ctx: dict[str, str]) -> str:
    values = {**ctx, "malformed_signature": TOOL_SIGNATURES[ctx["pagination"]]}
    return render(TESTS_SERVERS_PY, **values)


def _test_conftest_source(ctx: dict[str, str]) -> str:
    """Render ``conftest.py`` for ``ctx["pagination"]``/``ctx["auth_mode"]``."""
    auth_env_setup = render(_AUTH_ENV_SETUP[ctx["auth_mode"]], **ctx).rstrip("\n")
    page_bodies = render(_CONFORMANCE_PAGE_BODIES[ctx["pagination"]], **ctx)
    responses_fn = (
        _CONFORMANCE_RESPONSES_OAUTH
        if ctx["auth_mode"] in _OAUTH_AUTH_MODES
        else _CONFORMANCE_RESPONSES_STATIC
    )
    values = {
        **ctx,
        "auth_env_setup": auth_env_setup,
        "scripted_responses": page_bodies + "\n" + responses_fn,
    }
    return render(TESTS_CONFTEST_PY, **values)


def _test_api_client_source(ctx: dict[str, str]) -> str:
    """Render ``test_api_client.py`` for ``ctx["auth_mode"]``."""
    template = (
        TESTS_API_CLIENT_OAUTH_PY
        if ctx["auth_mode"] in _OAUTH_AUTH_MODES
        else TESTS_API_CLIENT_STATIC_PY
    )
    auth_env_setup = render(_AUTH_ENV_SETUP[ctx["auth_mode"]], **ctx).rstrip("\n")
    values = {
        **ctx,
        "auth_env_setup": auth_env_setup,
        "auth_header_assert": _AUTH_HEADER_ASSERT[ctx["auth_mode"]],
    }
    return render(template, **values)


def _write_tests(root: Path, ctx: dict[str, str]) -> None:
    tests = root / "tests"
    _write_generated_text(tests / "servers.py", _test_servers_source(ctx))
    _write_generated_text(tests / "conftest.py", _test_conftest_source(ctx))
    _write_generated_text(tests / "test_manifest.py", render(TESTS_MANIFEST_PY, **ctx))
    _write_generated_text(
        tests / "test_mcp_server.py", render(TESTS_MCP_SERVER_PY, **ctx)
    )
    _write_generated_text(
        tests / "test_credentials.py", render(TESTS_CREDENTIALS_PY, **ctx)
    )
    _write_generated_text(
        tests / "test_conformance.py", render(TESTS_CONFORMANCE_PY, **ctx)
    )
    _write_generated_text(tests / "test_api_client.py", _test_api_client_source(ctx))


def scaffold(
    package_name: str,
    *,
    display_name: str | None = None,
    description: str | None = None,
    domain: str = "reader",
    auth_mode: str = "bearer",
    pagination: str = "cursor",
    openapi: str | None = None,
    output_dir: str = ".",
    in_place: bool = False,
) -> Path:
    """Scaffold one connector package under ``output_dir``.

    Idempotent and non-destructive: an existing generated file with different
    content is preserved (see :func:`_write_generated_text`); a missing one is
    added.
    """
    ctx = build_context(
        package_name,
        display_name=display_name,
        description=description,
        domain=domain,
        auth_mode=auth_mode,
        pagination=pagination,
        openapi=openapi,
    )
    root = (
        Path(output_dir).resolve()
        if in_place
        else Path(output_dir).resolve() / package_name
    )
    root.mkdir(parents=True, exist_ok=True)

    _write_root_files(root, ctx)
    _write_package(root, ctx)
    _write_content(root, ctx)
    _write_tests(root, ctx)

    print(f"\nScaffolded {package_name!r} at {root}")
    print("Next steps:")
    print(f"  cd {root}")
    print("  uv sync")
    print("  python scripts/pin_tool_schema.py")
    print("  uv run --frozen python -m pytest -q")
    return root


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "package_name", help="kebab-case package name, e.g. example-connector"
    )
    parser.add_argument("--display-name", default=None)
    parser.add_argument("--description", default=None)
    parser.add_argument(
        "--domain",
        default="reader",
        help="snake_case name of the one MCP tool domain (default: reader)",
    )
    parser.add_argument(
        "--auth",
        dest="auth_mode",
        choices=AUTH_MODES,
        default="bearer",
        help="outbound auth the generated api_client.py builds (default: bearer)",
    )
    parser.add_argument(
        "--pagination",
        choices=PAGINATION_MODES,
        default="cursor",
        help="pagination style the generated tool and sync preset use (default: cursor)",
    )
    parser.add_argument(
        "--openapi",
        default=None,
        help="optional OpenAPI document; seeds the base URL and list path",
    )
    parser.add_argument("--output-dir", default=".")
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="scaffold directly into --output-dir instead of a new <package_name> subdirectory",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    scaffold(
        args.package_name,
        display_name=args.display_name,
        description=args.description,
        domain=args.domain,
        auth_mode=args.auth_mode,
        pagination=args.pagination,
        openapi=args.openapi,
        output_dir=args.output_dir,
        in_place=args.in_place,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
