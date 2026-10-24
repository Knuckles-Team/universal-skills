#!/usr/bin/env python3
"""Generate the minimal SDK-centralized connector tree (US-MCP-BUILDER-R011).

    python3 scaffold_connector.py example-mcp --output-dir /path/to/output

The output holds only what is specific to one connector: its tools, its
vendor-client constructor, its prompts, skills and ontology, its specs and
its docs. The SDK owns the server, the tests, the version, the health route and
the ontology shapes. The shared pipelines workflows own gates and release.
Output is deterministic: the same arguments yield byte-identical files, and
no date, user or host name is written.

Steps marked "agent-connector-sdk>=0.5.0" in the generated files rely on
SDK entry points (`run`, the conformance plugin) that the SDK ships in 0.5.0.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SDK_FLOOR = "0.5.0"
CORE_CLASS = "Concept"  # a class of the parent ontology (core-foundation)
VERBS = (
    ("get", "GET", "readOnlyHint", "Read one {thing} by id."),
    ("create", "POST", "", "Create a {thing}."),
    ("update", "PUT", "idempotentHint", "Replace a {thing} by id."),
    ("delete", "DELETE", "destructiveHint", "Delete a {thing} by id."),
)


def _names(fleet: str) -> dict[str, str]:
    if not re.fullmatch(r"[a-z][a-z0-9]*(-[a-z0-9]+)*", fleet):
        raise SystemExit(f"invalid fleet name {fleet!r}: use lower-case words joined by hyphens")
    short = fleet.removesuffix("-mcp").removesuffix("-api").removesuffix("-agent")
    pkg = fleet.replace("-", "_")
    return {
        "fleet": fleet,
        "pkg": pkg,
        "short": short,
        "upper": short.replace("-", "_").upper(),
        "Display": short.replace("-", " ").title(),
        "Class": short.replace("-", " ").title().replace(" ", ""),
        "spec_id": f"CONN-{fleet.upper()}",
    }


PYPROJECT = '''[build-system]
requires = ["setuptools>=84.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{fleet}"
version = "0.1.0"
description = "MCP connector for {Display}."
readme = "README.md"
requires-python = ">=3.12, <3.15"
dependencies = ["agent-connector-sdk[mcp]>={sdk},<1.0.0"]

[project.license]
text = "MIT"

# The server is the SDK's single run entry (agent-connector-sdk>={sdk}).
[project.scripts]
{fleet} = "agent_connector_sdk.cli:serve"

# The one declared identity: the entry-point name is the fleet name.
[project.entry-points."agent_connector_sdk.connector"]
{fleet} = "{pkg}"

[tool.setuptools.packages.find]
where = ["."]
include = ["{pkg}*"]

[tool.setuptools.package-data]
{pkg} = ["prompts/*.json", "skills/**/*", "ontology/**/*"]
'''

INIT = '"""MCP connector for {Display}."""\n'

MAIN = '''"""`python -m {pkg}` starts the server through the SDK."""

from agent_connector_sdk import run  # agent-connector-sdk>={sdk}

if __name__ == "__main__":
    run(package="{pkg}")
'''

CLIENT = '''"""The one vendor-client constructor. Transport, retries, TLS and auth are SDK components."""

from agent_connector_sdk.auth.static import bearer_auth
from agent_connector_sdk.config import load_config, setting
from agent_connector_sdk.http.client import create_http_client
from agent_connector_sdk.http.options import HttpClientOptions
from agent_connector_sdk.tls.resolve import resolve_tls_profile

_client = None


def get_client():
    """Return the governed HTTP client for {Display}.

    At agent-connector-sdk>={sdk} this body becomes
    `client_factory(env_prefix="{upper}", tls_name="{short}")`.
    """
    global _client
    if _client is None:
        load_config()
        _client = create_http_client(
            HttpClientOptions(
                base_url=setting("{upper}_BASE_URL", ""),
                auth=bearer_auth(setting("{upper}_TOKEN_REF", "")),
                tls=resolve_tls_profile("{short}"),
            )
        )
    return _client
'''

TOOLS = '''"""One MCP tool per API operation for {Display}.

Each HTTP method on each endpoint is its own tool. The tool name carries the
operation, the annotations carry the risk class (read, write or destructive),
and no tool routes on an `action` argument.
"""

from typing import Annotated, Any

from agent_connector_sdk.ingest.live_declaration import source_meta
from fastmcp import FastMCP
from pydantic import Field

from .client import get_client

READ = {{"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True}}
WRITE = {{"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True}}
IDEMPOTENT_WRITE = {{**WRITE, "idempotentHint": True}}
DESTRUCTIVE = {{"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True, "openWorldHint": True}}

#: Risk class of every tool; the SDK refuses to start with an unclassified tool.
CLASSES = {{
    "{short_snake}_get_item": "read",
    "{short_snake}_create_item": "write",
    "{short_snake}_update_item": "write",
    "{short_snake}_delete_item": "destructive",
}}


def register_tools(mcp: FastMCP) -> None:
    """Register every operation of the {Display} API on `mcp`."""

    @mcp.tool(
        name="{short_snake}_get_item",
        title="Get {Display} item",
        tags={{"{short}", "read"}},
        annotations=READ,
        meta=source_meta(
            source_id="{short_snake}_items",
            record_type="Item",
            id_field="id",
            ontology_class="{Class}Item",
            fields={{"name": "name"}},
        ),
    )
    def get_item(item_id: Annotated[str, Field(description="Item id.")]) -> Any:
        """GET /items/{{id}}: read one item."""
        return get_client().get(f"/items/{{item_id}}").json()

    @mcp.tool(
        name="{short_snake}_create_item",
        title="Create {Display} item",
        tags={{"{short}", "write"}},
        annotations=WRITE,
    )
    def create_item(name: Annotated[str, Field(description="Item name.")]) -> Any:
        """POST /items: create an item."""
        return get_client().post("/items", json={{"name": name}}).json()

    @mcp.tool(
        name="{short_snake}_update_item",
        title="Update {Display} item",
        tags={{"{short}", "write"}},
        annotations=IDEMPOTENT_WRITE,
    )
    def update_item(
        item_id: Annotated[str, Field(description="Item id.")],
        name: Annotated[str, Field(description="New item name.")],
    ) -> Any:
        """PUT /items/{{id}}: replace an item."""
        return get_client().put(f"/items/{{item_id}}", json={{"name": name}}).json()

    @mcp.tool(
        name="{short_snake}_delete_item",
        title="Delete {Display} item",
        tags={{"{short}", "destructive"}},
        annotations=DESTRUCTIVE,
    )
    def delete_item(item_id: Annotated[str, Field(description="Item id.")]) -> Any:
        """DELETE /items/{{id}}: delete an item."""
        return get_client().delete(f"/items/{{item_id}}").json()
'''

PROMPT = {
    "description": "Operate the {Display} connector.",
    "identity": {"role": "{Display} operator", "goal": "Use the {Display} tools safely."},
    "metadata": {"topic": "{short}"},
    "prompt_version": "1",
    "serves": "{Class}Item",
    "instructions": {
        "core_directive": "Read with the get tools first. Ask before any create, update or delete tool."
    },
}

SKILL = """---
name: {short}-operations
description: Operate {Display} through its MCP tools. Use when reading or changing {Display} items.
---

# {Display} operations

1. Read the item with `{short_snake}_get_item`.
2. Change it with `{short_snake}_create_item` or `{short_snake}_update_item`.
3. Delete with `{short_snake}_delete_item` only after the user confirms.
"""

ONTOLOGY = """@prefix : <http://knuckles.team/kg#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# {Display} classes. Every class extends a core class of the parent ontology
# through rdfs:subClassOf. The pack never imports the parent ontology.

:{Class}Item a owl:Class ;
    rdfs:subClassOf :{core} ;
    rdfs:label "{Display} Item" ;
    rdfs:comment "An item served by the {Display} API." .

:{short_camel}RelatedTo a owl:ObjectProperty ;
    rdfs:label "{Display} related to" ;
    rdfs:comment "Links a {Display} item to any core concept it describes." ;
    rdfs:domain :{Class}Item ;
    rdfs:range :{core} .
"""

README = """# {fleet}

MCP connector for {Display}. The SDK serves everything over MCP: tools, prompts,
skills, ontology resources and the data-source declaration (`connector://resources`).

    pip install {fleet}
    {fleet} --transport stdio

Settings: `{upper}_BASE_URL`, `{upper}_TOKEN_REF` (an `env://` or `openbao://` reference).
"""

AGENTS = """# {fleet}

## Connector

{Display} connector. One tool per API operation in `{pkg}/tools.py`; the vendor client
constructor is `{pkg}/client.py`. Everything else is an SDK component.

<!-- The standard agent-contract section is delivered by the shared pipelines hook. -->
"""

PRECOMMIT = """repos:
  - repo: https://github.com/Knuckles-Team/pipelines
    rev: main
    hooks:
      - id: connector-name
        args: [--strict]
      - id: release-standard
"""

PIPELINE = """name: Build|Upload|Release Python Package

on:
  push:
    branches:
      - 'main'

permissions:
  contents: read

jobs:
  publish-pypi:
    uses: Knuckles-Team/pipelines/.github/workflows/python_pipeline.yml@main
    permissions:
      contents: write
    secrets:
      PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
  publish-docker:
    needs: publish-pypi
    uses: Knuckles-Team/pipelines/.github/workflows/container_pipeline.yml@main
    permissions:
      contents: read
    secrets:
      DOCKER_REGISTRY: ${{ secrets.DOCKER_REGISTRY }}
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
      DOCKER_REPOSITORY: ${{ secrets.DOCKER_REPOSITORY }}
"""

CONNECTOR_PR = """name: Connector PR

on: pull_request

concurrency:
  group: pr-${{ github.workflow }}-${{ github.event.pull_request.number }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  gates:
    uses: Knuckles-Team/pipelines/.github/workflows/connector_pr_pipeline.yml@main
"""

# The shared container workflow renders the image; this file is the one the
# release-standard gate requires until pipelines renders it at build time.
DOCKERFILE = """# syntax=docker/dockerfile:1
FROM python:3.14-slim AS mcp
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN pip install --only-binary :all: "{fleet}[mcp]" \\
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin mcp
USER 10001
CMD ["{fleet}"]
"""

TEST = '''"""Tests for the {Display} tool logic. SDK behavior is tested by the SDK plugin."""

import pytest

pytest.importorskip("fastmcp")


@pytest.mark.asyncio
async def test_one_tool_per_operation():
    from fastmcp import Client, FastMCP

    from {pkg}.tools import register_tools

    mcp = FastMCP("test")
    register_tools(mcp)
    async with Client(mcp) as client:
        names = sorted(tool.name for tool in await client.list_tools())
    assert names == sorted(
        f"{short_snake}_{{op}}_item" for op in ("get", "create", "update", "delete")
    )
'''

SPEC_FILES = {
    "spec.md": """# {spec_id} — {Display} connector

Owner: {fleet}.

## Outcome

The {Display} connector serves one MCP tool per {Display} API operation.

## Scope

In scope: the operations, source mappings, prompts, skills and ontology of {Display}.
Out of scope: server start, tests of SDK behavior, version files and gates (the SDK and pipelines own them).

## Why a new spec

No spec in this repository owns the {Display} operations.
""",
    "plan.md": """# {spec_id} — Plan

## Architecture

`{pkg}/tools.py` registers the tools. `{pkg}/client.py` builds the governed client. The SDK run entry serves them.

## Interfaces

Entry point `agent_connector_sdk.connector`: `{fleet} = "{pkg}"`.
""",
    "requirements.md": """# {spec_id} — Requirements

| ID | Requirement | Acceptance |
|---|---|---|
| `{spec_id}-R001` | **One tool per operation.** The connector must register each {Display} API operation as its own tool. | `tests/test_tools.py::test_one_tool_per_operation` |
""",
    "tasks.md": """# {spec_id} — Tasks

- [ ] **{spec_id}-R001:** One tool per operation.
""",
    "test-spec.md": """# {spec_id} — Test specification

| Test ID | Requirement | Proving test |
|---|---|---|
| T-001 | `{spec_id}-R001` | `tests/test_tools.py::test_one_tool_per_operation` |
""",
}


def _status(spec_id: str, fleet: str) -> str:
    row = {
        "id": f"{spec_id}-R001",
        "title": "One tool per operation",
        "delivery_state": "SPECIFIED",
        "landed_in": [],
        "verified_by": [],
    }
    status = {
        "schema_version": 2,
        "spec_id": spec_id,
        "owner_repo": fleet,
        "delivery_state": "SPECIFIED",
        "requirement_ids": [row["id"]],
        "requirements": [row],
    }
    return json.dumps(status, indent=2) + "\n"


def tree(fleet: str) -> dict[str, str]:
    """Return every generated file as relative path -> text."""
    n = _names(fleet)
    n.update(sdk=SDK_FLOOR, core=CORE_CLASS, short_snake=n["short"].replace("-", "_"), short_camel=n["Class"][0].lower() + n["Class"][1:])
    pkg, spec = n["pkg"], f"specs/{fleet}"

    def fmt(text: str) -> str:
        return text.format(**n)

    prompt = re.sub(r"\{(\w+)\}", lambda m: n.get(m.group(1), m.group(0)), json.dumps(PROMPT, indent=2))
    files = {
        "pyproject.toml": PYPROJECT,
        "README.md": README,
        "AGENTS.md": AGENTS,
        ".pre-commit-config.yaml": PRECOMMIT.replace("{", "{{").replace("}", "}}"),
        ".github/workflows/pipeline.yml": PIPELINE.replace("{", "{{").replace("}", "}}"),
        ".github/workflows/connector-pr.yml": CONNECTOR_PR.replace("{", "{{").replace("}", "}}"),
        "docker/Dockerfile": DOCKERFILE,
        f"{pkg}/__init__.py": INIT,
        f"{pkg}/__main__.py": MAIN,
        f"{pkg}/client.py": CLIENT,
        f"{pkg}/tools.py": TOOLS,
        f"{pkg}/prompts/{n['short']}-operator.json": "",
        f"{pkg}/skills/{n['short']}-operations/SKILL.md": SKILL,
        f"{pkg}/ontology/{n['short']}.ttl": ONTOLOGY,
        "tests/test_tools.py": TEST,
        "specs/README.md": "# Specifications\n\n- [`{spec_id}`]({fleet}/spec.md) — {Display} connector tools.\n",
    }
    out = {path: fmt(text) for path, text in files.items()}
    out[f"{pkg}/prompts/{n['short']}-operator.json"] = prompt + "\n"
    for name, text in SPEC_FILES.items():
        out[f"{spec}/{name}"] = fmt(text)
    out[f"{spec}/status.json"] = _status(n["spec_id"], fleet)
    return dict(sorted(out.items()))


def scaffold(fleet: str, output_dir: Path) -> list[Path]:
    """Write the tree under `output_dir/<fleet>`; never overwrite an existing file."""
    root = output_dir / fleet
    written: list[Path] = []
    for rel, text in tree(fleet).items():
        path = root / rel
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("fleet_name", help="fleet name, for example example-mcp")
    parser.add_argument("--output-dir", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    written = scaffold(args.fleet_name, args.output_dir)
    print(f"{args.fleet_name}: wrote {len(written)} files under {args.output_dir / args.fleet_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
