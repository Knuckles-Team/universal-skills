---
name: agent-package-builder
domain: agent-tools
skill_type: skill
description: >-
  Scaffold a new MCP connector package on agent-connector-sdk: a real API
  client built only from agent_connector_sdk.http/tls/auth (bearer, basic,
  api_key, client_credentials or delegated auth; cursor/page/offset
  pagination), a governed server (create_mcp_server + register_tool_surface)
  whose tool calls that client, content served as native MCP primitives
  (skills, prompts, ontology, SHACL shapes, manifest), a connector_manifest.yml
  with a valid sync preset, env://openbao:// credential references, pages/
  documentation, and pre-commit/CI wired to the shared workspace hook bundle.
  Use for brand-new connector packages (RF-ADR-009 phase 7); it never
  generates an agent-utilities dependency.
license: MIT
tags: [agent, connector, scaffold, mcp, agent-connector-sdk, epistemic-graph]
metadata:
  version: '1.3.1'
---

# Agent Package Builder

Scaffold a connector package that depends on
[`agent-connector-sdk`](https://github.com/Knuckles-Team/agent-connector-sdk)
and `epistemic-graph` only (RF-ADR-009, workspace phase 7). The definitive
generated-file contract is [`PARITY_MANIFEST.md`](PARITY_MANIFEST.md).

**Never use this skill to scaffold `agent-connector-sdk` or `graph-os`
themselves** (RF-ADR-009 section 8) — it generates a *consumer* of the SDK, a
72-connector-fleet-shaped package, not the SDK itself.

## Invocation

```bash
python3 scripts/scaffold_package.py <package-name> \
  [--display-name ...] [--description ...] [--domain reader] \
  [--auth bearer|basic|api_key|client_credentials|delegated] \
  [--pagination cursor|page|offset] [--openapi <file>] \
  [--output-dir ...] [--in-place]
```

`--domain` names the one MCP tool domain the scaffold ships (`<pkg>_<domain>`,
default `reader`); rename or add domains under `<pkg>/mcp/` as the connector
grows. `--auth` (default `bearer`) picks which `agent_connector_sdk.auth`
helper `<pkg>/api_client.py`'s `_auth()` builds. `--pagination` (default
`cursor`) picks the tool's one pagination parameter and the matching
`preset_pagination`-equivalent fields in the sync preset. `--openapi` is
optional and best-effort: it seeds the base URL and one list-operation path
from `servers[0].url` and the first `GET` path in a small OpenAPI document;
without it the generator emits `https://api.example.invalid` and
`/<domain>` placeholders. The generator never requests or writes a person's
name or email, never generates a `.env` file, and never invents a customized
ontology, endpoint, or credential value — those are operator inputs resolved
as `env://`/`openbao://` references at runtime.

## Workflow

### 1. Gather requirements

| Input | Required | Default |
|---|---:|---|
| package name | yes | — |
| display name | no | derived from package name |
| one-line description | no | generated |
| MCP tool domain | no | `reader` |
| outbound auth mode | no | `bearer` |
| pagination style | no | `cursor` |
| OpenAPI document (base URL + list path hint) | no | none — placeholders |
| output directory | no | current directory |

### 2. Scaffold, then complete the two steps a generator cannot do for you

```bash
python3 scripts/scaffold_package.py example-connector
cd example-connector
uv sync
python scripts/pin_tool_schema.py   # required: pins the live tool schema fingerprint
uv run --frozen python -m pytest -q
```

`scripts/pin_tool_schema.py` starts the live tool contract at a placeholder
(`connector_manifest.yml`'s `sync[0].tool_schema_sha256` and
`connectors/tool_schema_fingerprints.json` share the same placeholder string,
so the manifest/preset/fingerprint structural cross-check passes immediately)
and pins it to the real compatibility fingerprint once the server can run.
Skipping this step is safe for `tests/test_manifest.py` and for the default
`pytest -q` run: `tests/test_conformance.py`'s test is marked
`@pytest.mark.integration` (its fixtures build the real server, whose tool
calls the real vendor API, so it needs real credentials configured; run it
explicitly with `-m integration`) and is deselected by `pytest.ini`'s default
`-m "not integration"`. Once run, an unpinned fingerprint fails it closed, by
design — `McpToolSourceAdapter.discover()` never extracts through an
unverified tool.

The scaffold is idempotent and non-destructive on rerun: an existing
project-owned file with different content is preserved; a missing generated
file is added (see `PARITY_MANIFEST.md`'s rejection gate for what a
regenerated file must never contain).

### 3. What gets generated

- `pyproject.toml` depending on `agent-connector-sdk` and `epistemic-graph`
  only, one `<package>-mcp` console script;
- `<pkg>/api_client.py`, the governed API client built only from
  `agent_connector_sdk.http`/`tls`/`auth` — never raw `httpx`/`requests`:
  `_auth()` (the one function `--auth` varies), `build_client()` (the async
  composition root: `create_async_http_client` + `HttpClientOptions` +
  `resolve_tls_profile`), and `build_client_for(base_url)` (the sync factory
  the SDK's HTTP conformance kit drives);
- `<pkg>/mcp_server.py` built from the SDK's `create_mcp_server` +
  `register_tool_surface`, serving `ConnectorContent` (this package's
  `skills/`, `prompts/`, `ontology/`, `connector_manifest.yml`) as native MCP
  primitives — `tools/list`, `skill://…`, `prompts/list`, `ontology://…`,
  `shapes://…`, `manifest://connector`. There is no second export channel;
- `<pkg>/mcp/mcp_<domain>.py`'s one tool calls `api_client.build_client()` and
  returns an `agent_connector_sdk.http.pagination.ToolPage`, one pagination
  parameter (`cursor`, `page`, or `offset`) matching `--pagination`;
- `<pkg>/credentials.py` wiring `env://`/`openbao://` references through
  `agent_connector_sdk.credentials` for ad hoc use — `api_client.py`'s
  `_auth()` calls the SDK's `auth.*` helpers directly instead;
- `connector_manifest.yml` with one governed `sync` preset (`params_style:
  "args"`, no `action`, pagination fields matching `preset_pagination`,
  pinned by `tool_schema_sha256`), cross-checked against
  `connectors/mcp_source_presets.json` and
  `connectors/tool_schema_fingerprints.json`;
- `.pre-commit-config.yaml` with the standard formatting/typing/lock hooks
  pinned to reviewed revisions, plus one block referencing the shared
  workspace gate bundle (`https://github.com/Knuckles-Team/pipelines`) by
  hook id with `rev: REPLACE_WITH_SHARED_HOOKS_REV` — **no gate script
  (complexity, KISS, duplication, secret-history, sanitizer, tracked-privacy,
  root-hygiene, dependency-audit, orphan-module) is ever copied into the
  package.** That block cannot run until the SHARED-HOOKS lane publishes the
  bundle; report which hooks fail to resolve rather than working around it;
- `pages/` + `mkdocs.yml` (`docs_dir: pages`, no local `theme:`/
  `markdown_extensions:` — those are inherited from the shared pipelines
  theme) — there is no `/docs`;
- `pages/agent-readiness.json` + `pages/agent-readiness.schema.json` (a
  verbatim copy of the canonical schema) — the applicability declaration both
  universal-skills' generator and the pipelines readiness TCK validate;
- `scripts/generate_agent_readiness.py`, which regenerates the committed,
  root-level `llms.txt`, `llms-sections/`, and `markdown-mirror-manifest.json`
  from `pages/agent-readiness.json` by delegating to the installed
  universal-skills builder (`uv sync --group docs` first; never vendored);
- `.github/workflows/pages.yml`, a thin caller of the shared reusable
  workflow `Knuckles-Team/pipelines/.github/workflows/pages_pipeline.yml`
  (pinned to a full commit SHA) with `content_source: pages`,
  `shared_theme_enabled: true`, `agent_readiness_enabled: true` — no local
  mkdocs-build-and-deploy steps of its own;
- `tests/` mirroring `agent-connector-sdk`'s own fixture pattern: manifest
  validity, MCP server content listing, credential resolution, the SDK's
  source-adapter conformance kit, and `tests/test_api_client.py` — the SDK's
  HTTP client conformance kit (`bearer`/`basic`/`api_key`) plus a
  `ScriptedHttpServer` end-to-end proof of the real tool for every `--auth`
  mode (auth header sent, a paginated call, a `HttpProblemError`-mapped 404).

### 4. Validate before handoff

```bash
uv run --frozen python -m ruff check .
uv run --frozen python -m ruff format --check .
uv run --frozen python -m mypy <pkg>
uv run --frozen python -m pytest -q
uv run --frozen python -c "from agent_connector_sdk.manifest.loader import require_valid_connector_package; from pathlib import Path; require_valid_connector_package(Path('.'))"
uv run --group docs python scripts/generate_agent_readiness.py   # after touching pages/*.md or agent-readiness.json
pre-commit run --all-files            # everything except the SHARED-HOOKS block, until it publishes
```

Also verify:

- every file in `PARITY_MANIFEST.md` exists;
- `pyproject.toml` names `agent-connector-sdk` and `epistemic-graph` only —
  no `agent-utilities` dependency, import, or entry point anywhere in the tree;
- `connector_manifest.yml`'s `sync[].tool_schema_sha256` is a real pinned
  value (run `scripts/pin_tool_schema.py`), not the placeholder;
- no `.env`, raw credential, `SSL_VERIFY`, or `verify=False` path exists;
- `<pkg>/api_client.py` is the only module making outbound requests, built
  only from `agent_connector_sdk.http`/`tls`/`auth` — no raw `httpx`/
  `requests` call anywhere in the tree;
- documentation lives under `pages/`, never `docs/`.

Do not publish, push, deploy, or create remote resources without the user's
explicit authorization.
