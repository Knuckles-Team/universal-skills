#!/usr/bin/env python3
"""Generate the minimal SDK-centralized connector tree (US-MCP-BUILDER-R011).

    python3 scaffold_connector.py example-mcp --output-dir /path/to/output

The output holds only what is specific to one connector: its tools, its
vendor-client constructor, its prompts, skills and ontology, its specs, its
minimal Pages source and its delivery callers. The SDK owns the server, the
tests, the version, the health route and the ontology shapes. The shared
pipelines workflows own gate and release implementations; this scaffold emits
only the connector-owned references to them.
Output is deterministic: the same arguments yield byte-identical files, and
no date, user or host name is written.

The generated package requires scion-sdk>=0.5.1 (`Connector`, `run`,
`load_declaration`, `client_factory` and the pytest conformance plugin).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SDK_FLOOR = "0.5.1"
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


PYPROJECT = """[build-system]
requires = ["setuptools>=84.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{fleet}"
version = "0.1.0"
description = "MCP connector for {Display}."
readme = "README.md"
requires-python = ">=3.12, <3.15"
dependencies = ["scion-sdk[mcp]>={sdk},<0.6"]

[project.license]
text = "MIT"

# The SDK serves the declared connector: `{fleet}` starts the server.
[project.scripts]
{fleet} = "agent_connector_sdk.cli:serve"

# The one declared identity: the entry-point name is the fleet name.
[project.entry-points."agent_connector_sdk.connector"]
{fleet} = "{pkg}:connector"

[tool.setuptools.packages.find]
where = ["."]
include = ["{pkg}*"]

[tool.setuptools.package-data]
{pkg} = ["prompts/*.json", "skills/**/*", "ontology/**/*"]
"""

INIT = """\"\"\"MCP connector for {Display}.\"\"\"

from agent_connector_sdk.connector import Connector

from .api_client import Api
from .auth import get_client

connector = Connector(
    api=Api,
    get_client=get_client,
    instructions="Operate {Display}. Read before you change; confirm before you delete.",
)
"""

MAIN = """from agent_connector_sdk import run

if __name__ == "__main__":
    run()
"""

AUTH = """\"\"\"The one place the {Display} client is declared, from SDK components.\"\"\"

from agent_connector_sdk.auth.declare import Bearer, client_factory

from .api_client import Api

# Auth scheme, TLS profile, delegation, retries and credential rotation are SDK
# components. Swap `Bearer` for `ApiKey`, `Basic`, `ClientCredentials`,
# `RefreshToken`, `SessionLogin` or `NoAuth` to match the {Display} API.
_http = client_factory(
    url_env="{upper}_BASE_URL",
    auth=Bearer(env="{upper}_TOKEN"),
    tls="{short}",
    delegation=True,
)


def get_client() -> Api:
    \"\"\"Return the {Display} client over the SDK-governed HTTP client.\"\"\"
    return Api(_http())
"""

API_CLIENT = """\"\"\"The {Display} API operations. The SDK serves one MCP tool per public method.

The HTTP verb in each docstring sets the tool's risk class: GET is read-only,
PUT and POST write, DELETE is destructive and asks the caller to confirm.
\"\"\"

from typing import Any


class Api:
    \"\"\"One method per {Display} API operation.\"\"\"

    def __init__(self, http: Any) -> None:
        self._http = http

    def get_item(self, item_id: str) -> dict[str, Any]:
        \"\"\"GET /items/{{item_id}}: read one item by id.\"\"\"
        return self._http.get(f"/items/{{item_id}}").json()

    def create_item(self, name: str) -> dict[str, Any]:
        \"\"\"POST /items: create an item.\"\"\"
        return self._http.post("/items", json={{"name": name}}).json()

    def update_item(self, item_id: str, name: str) -> dict[str, Any]:
        \"\"\"PUT /items/{{item_id}}: replace an item by id.\"\"\"
        return self._http.put(f"/items/{{item_id}}", json={{"name": name}}).json()

    def delete_item(self, item_id: str) -> dict[str, Any]:
        \"\"\"DELETE /items/{{item_id}}: delete an item by id.\"\"\"
        return self._http.delete(f"/items/{{item_id}}").json()
"""

SOURCES = """\"\"\"Declared data sources: typed data the SDK reads with `load_declaration`.\"\"\"

from agent_connector_sdk.ingest.live_declaration import source_meta

SCHEMA_VERSION = 1

SOURCES = (
    source_meta(
        tool="{short_snake}_get_item",
        source_id="{short_snake}_items",
        record_type="{Class}Item",
        id_field="id",
        ontology_class="{Class}Item",
        fields={{"name": "name"}},
    ),
)
"""

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
skill_type: skill
domain: connector
description: Operate {Display} through its MCP tools. Use when reading or changing {Display} items.
---

# {Display} operations

1. Read the item with `{short_snake}_get_item`.
2. Change it with `{short_snake}_create_item` or `{short_snake}_update_item`.
3. Delete with `{short_snake}_delete_item` only after the user confirms.
"""

DEVELOPMENT_SKILL = """---
name: {fleet}-development
skill_type: skill
domain: development
description: >-
  Develop, test, gate, and release the {fleet} connector. Use when changing
  its API mappings, MCP tools, packaging, documentation, or repository gates.
license: MIT
tags: [{fleet}, development, connector, test, gates]
tier: repository
metadata:
  author: Genius
  version: '0.1.0'
---

# {fleet} development

This repository owns the {Display} transport, mappings, MCP tools and package
content. Shared connector contracts, authentication and transports belong to
`agent-connector-sdk`; admission, serving and durable graph state belong to
their owning repositories. Keep provider credentials, endpoints and raw data
out of source, logs and skill content.

## Rapid delivery: the 5-minute contract

Specs are designed before implementation. Deliver small, reviewable slices and
cite the owning spec row in the commit trailer.

- Find the owning row first with `git grep -n "<term>" -- specs` and extend that
  spec before adding new requirement text.
- Reuse existing SDK clients, transport policies and tool factories. Do not
  create a second implementation of a connector capability.
- Keep changes scoped to this connector. A change owned by the SDK, Arbora or
  the knowledge graph belongs in that repository instead.
- Every delivered requirement needs a bound test. Spec status is computed by
  `pipelines-hook spec-status` at read time; `status.json` is never committed.
- One logical change per commit, with `Spec: <ID>` and the assisting agent
  trailer adjacent in the final paragraph.

## Setup and gates

On the first checkout, create the lockfile before using locked commands:

```bash
uv lock
uv sync --locked
```

Run the repository gate from the checkout root:

```bash
uvx pre-commit run --all-files
```

For focused feedback, run the relevant tests with the repository's pinned
environment. The canonical `.pre-commit-config.yaml` delegates
`connector-standard`, `secrets`, `spec`, `tests-fast` and
`dependency-readiness` to `Knuckles-Team/pipelines` at `rev: main`; do not
replace those shared hooks with local copies or bypass a failing check.

## Connector-specific checks

- Keep the MCP surface aligned with `agent-connector-sdk`.
- Validate environment and TLS settings before provider calls.
- Mock external provider calls in tests; never use live credentials in a local gate.
- Keep `{pkg}/skills/` package data intact when adding skills.
- Documentation lives under `pages/` and is published by the shared Pages
  workflow; source status records live under `specs/`.
- The scaffold leaves `shared_theme_enabled: false` because the shared Pages
  workflow requires canonical theme outputs in the content tree. If this
  connector adopts the shared theme, use the pinned pipelines checkout and its
  `scripts/sync_mkdocs_theme.py sync` command to generate the assets, review
  them, commit them, and only then enable the caller flag. Never hand-copy or
  reimplement the provider assets.

## Delivery discipline

Work in a real Git worktree based on `origin/main`. Inspect the complete diff,
stage only reviewed paths and verify `git status --short` after every gate. Do
not use `git stash`, `git add -A` or `git add .`; do not claim Pages publication
until a successful exact-source workflow run and the public page are both
observed.
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

Settings: `{upper}_BASE_URL`, `{upper}_TOKEN`.
"""

AGENTS = """# {fleet}

## Connector

{Display} connector. The operations are the methods of `{pkg}/api_client.py`; the SDK
serves one tool per method. `{pkg}/auth.py` builds the client, `{pkg}/connector_sources.py`
declares the data sources. Everything else is an SDK component or a shared pipelines file.

## Release

Bump first, tag last. A tag whose commit still carries the previous version rebuilds the
old version under the new tag and PyPI refuses it; the shared `python_pipeline.yml` guard
fails when the tag differs from the package version or the version is already on PyPI.

1. Bump the version first: it lives in `pyproject.toml` (and `.bumpversion.cfg` when the
   repo has one; then use `bump2version --config-file .bumpversion.cfg --allow-dirty --no-commit --no-tag <part>`).
   Refresh the lock and any recorded fixture that embeds the version in the same PR.
2. Merge the bump PR.
3. At the merged commit, check `git show <commit>:pyproject.toml` carries the intended
   version and that it is unpublished:
   `curl -s -o /dev/null -w '%{{http_code}}' https://pypi.org/pypi/{fleet}/X.Y.Z/json` must print `404`.
4. Only then push the tag `vX.Y.Z` on that commit.
5. Confirm the wheel and sdist are on PyPI.
6. Tag on the wrong commit and nothing published: delete the tag and re-tag. Anything
   published: cut the next patch; never move a published tag.
"""

# The reference pre-commit configuration of pipelines (templates/connector/pre-commit-config.yaml).
PRECOMMIT = """default_install_hook_types: [pre-commit, pre-push]
default_stages: [pre-commit]
repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: 3e8a8703264a2f4a69428a0aa4dcb512790b2c8c # v6.0.0
  hooks:
  - id: trailing-whitespace
  - id: end-of-file-fixer
  - id: check-merge-conflict
  - id: check-yaml
    args: [--unsafe]
  - id: check-toml
  - id: check-json
  - id: detect-private-key
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: cb8c523fd4835aba42af70f4cad5568db4df0b6c # v0.16.0
  hooks:
  - id: ruff-check
  - id: ruff-format
- repo: https://github.com/Knuckles-Team/pipelines
  rev: main
  hooks:
  - id: connector-standard
  - id: secrets
  - id: spec
    stages: [pre-push]
  - id: tests-fast
    stages: [pre-push]
  - id: dependency-readiness
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
    with:
      connector: true
    permissions:
      contents: write
    secrets:
      PYPI_API_TOKEN: ${{{{ secrets.PYPI_API_TOKEN }}}}
  publish-docker:
    needs: publish-pypi
    uses: Knuckles-Team/pipelines/.github/workflows/container_pipeline.yml@main
    with:
      render_connector: true
    permissions:
      contents: read
    secrets:
      DOCKER_REGISTRY: ${{{{ secrets.DOCKER_REGISTRY }}}}
      DOCKER_USERNAME: ${{{{ secrets.DOCKER_USERNAME }}}}
      DOCKER_PASSWORD: ${{{{ secrets.DOCKER_PASSWORD }}}}
      DOCKER_REPOSITORY: ${{{{ secrets.DOCKER_REPOSITORY }}}}
"""

CONNECTOR_PR = """name: Connector PR

on: pull_request

concurrency:
  group: pr-${{{{ github.workflow }}}}-${{{{ github.event.pull_request.number }}}}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  gates:
    uses: Knuckles-Team/pipelines/.github/workflows/connector_pr_pipeline.yml@main
"""

SPEC_DASHBOARD = """{{
  "version": 1,
  "sources": [
    {{
      "glob": "specs/*/status.json",
      "kind": "spec"
    }}
  ]
}}
"""

PAGES = """name: Deploy GitHub Pages

on:
  push:
    branches:
      - main
    paths:
      - 'pages/**'
      - 'specs/**'
      - '.github/spec-dashboard.json'
      - '.github/workflows/pages.yml'
  workflow_dispatch: {{}}

permissions:
  contents: read

jobs:
  publish-pages:
    uses: Knuckles-Team/pipelines/.github/workflows/pages_pipeline.yml@main
    with:
      content_source: pages
      # Canonical theme assets are not scaffolded. Opt in only after running
      # pipelines/scripts/sync_mkdocs_theme.py sync from a pinned checkout.
      shared_theme_enabled: false
      spec_dashboard_enabled: true
      spec_dashboard_config: .github/spec-dashboard.json
    permissions:
      contents: read
      pages: write
      id-token: write
"""

PAGES_INDEX = """# {fleet}

MCP connector for {Display}. The shared Pages workflow publishes this source
tree and the spec-delivery dashboard.
"""

TEST = """\"\"\"Tests of the {Display} client logic. SDK behavior is tested by the SDK plugin.\"\"\"

from unittest.mock import MagicMock

from {pkg}.api_client import Api


def test_each_operation_calls_its_endpoint():
    http = MagicMock()
    api = Api(http)
    api.get_item("1")
    api.create_item("a")
    api.update_item("1", "b")
    api.delete_item("1")
    http.get.assert_called_once_with("/items/1")
    http.post.assert_called_once_with("/items", json={{"name": "a"}})
    http.put.assert_called_once_with("/items/1", json={{"name": "b"}})
    http.delete.assert_called_once_with("/items/1")
"""

SPEC_FILES = {
    "spec.md": """# {spec_id} — {Display} connector

Owner: {fleet}.

## Outcome

The {Display} connector serves one MCP tool per {Display} API operation.

## Scope

In scope: the operations, source mappings, prompts, skills and ontology of {Display}.
Out of scope: server start, tests of SDK behavior, version files, container files and gates (the SDK and pipelines own them).

## Why a new spec

No spec in this repository owns the {Display} operations.
""",
    "plan.md": """# {spec_id} — Plan

## Architecture

`{pkg}/api_client.py` holds one method per operation. `{pkg}/auth.py` builds the client. The SDK `Connector` and `run` entry serve one tool per method.

## Interfaces

Entry point `agent_connector_sdk.connector`: `{fleet} = "{pkg}:connector"`.
""",
    "requirements.md": """# {spec_id} — Requirements

| ID | Requirement | Acceptance |
|---|---|---|
| `{spec_id}-R001` | **One tool per operation.** The connector must register each {Display} API operation as its own tool. | `tests/test_api_client.py::test_each_operation_calls_its_endpoint` |
""",
    "tasks.md": """# {spec_id} — Tasks

- [ ] **{spec_id}-R001:** One tool per operation.
""",
    "test-spec.md": """# {spec_id} — Test specification

| Test ID | Requirement | Proving test |
|---|---|---|
| T-001 | `{spec_id}-R001` | `tests/test_api_client.py::test_each_operation_calls_its_endpoint` |
""",
}


CONSTITUTION = """# {Display} connector constitution

This connector inherits the [organization constitution](https://github.com/Knuckles-Team/pipelines/blob/main/.specify/memory/constitution.md) version 1.0.0. Every article of that constitution applies here. This file adds only the rules of this connector.

**Inherits**: organization constitution v1.0.0 | **Version**: 1.0.0 | **Ratified**: [date] | **Last amended**: [date]

## Organization standards

- [Spec standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/spec-standard.md): one owning spec per capability, computed states, `Spec:` trailers.
- [Ecosystem boundaries](https://github.com/Knuckles-Team/pipelines/blob/main/reference/ecosystem-boundaries.md): which repository owns which requirement.
- [Wording standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/ste.md): sentences of 20 words or fewer, with `must`, `should`, or `may`.

## Repository articles

### R-I. One external system

This connector wraps {Display} and nothing else. Shared helpers, domain maths and stores belong to their owners.

**Enforced by:** `connector-surface-audit` and `sdk-conformance` in pipelines.

**Plan check:** Does the change touch only the calls, mappings and tools of {Display}?

### R-II. One tool per API operation

Each API operation is one public method of `Api` and one served tool. No tool condenses operations behind an action or parameter dispatch.

**Enforced by:** `scripts/check_tool_parity.py` in the `mcp-builder` skill and `connector-surface-audit`.

**Plan check:** Does every new operation add exactly one method and one tool?

### R-III. The SDK is the only dependency

The connector depends on the connector SDK alone. Auth, TLS, paging, limits and optional dependencies come from SDK components and extras.

**Enforced by:** `sdk-conformance`, `connector-graphql` and `connector-standard` in pipelines.

**Plan check:** Does the change add no direct dependency and no copy of an SDK capability?

## Repository limits

This connector sets no numeric limit of its own. It follows the organization limits table.

Amend this file in a reviewed change. State the impact in the pull request. When the organization constitution changes its version, update the **Inherits** line in the same change.
"""


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
        ".pre-commit-config.yaml": PRECOMMIT,
        ".github/spec-dashboard.json": SPEC_DASHBOARD,
        ".github/workflows/pipeline.yml": PIPELINE,
        ".github/workflows/connector-pr.yml": CONNECTOR_PR,
        ".github/workflows/pages.yml": PAGES,
        "pages/index.md": PAGES_INDEX,
        f"{pkg}/__init__.py": INIT,
        f"{pkg}/__main__.py": MAIN,
        f"{pkg}/api_client.py": API_CLIENT,
        f"{pkg}/auth.py": AUTH,
        f"{pkg}/connector_sources.py": SOURCES,
        f"{pkg}/skills/{n['short']}-operations/SKILL.md": SKILL,
        f"{pkg}/skills/{fleet}-development/SKILL.md": DEVELOPMENT_SKILL,
        f"{pkg}/ontology/{n['short']}.ttl": ONTOLOGY,
        "tests/test_api_client.py": TEST,
        ".specify/memory/constitution.md": CONSTITUTION,
        "specs/README.md": "# Specifications\n\n- [`{spec_id}`]({fleet}/spec.md) — {Display} connector tools.\n",
    }
    out = {path: fmt(text) for path, text in files.items()}
    out[f"{pkg}/prompts/{n['short']}-operator.json"] = prompt + "\n"
    for name, text in SPEC_FILES.items():
        out[f"{spec}/{name}"] = fmt(text)
    out[".gitignore"] = "# Spec status is computed at read time, never committed.\nspecs/*/status.json\n"
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
    print("Before the first push run: pipelines-hook connector-name --strict")
    print("  and: pipelines-hook connector-ontology-map graph-check (see SKILL.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
