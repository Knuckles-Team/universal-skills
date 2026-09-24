---
name: agent-connector-sdk-development
domain: development
skill_type: skill
description: >-
  Develop inside agent-connector-sdk — the only connector path in the GraphOS
  ecosystem (MCP server construction, manifests, content packs, certification,
  the connector-sync runner, governed HTTP/TLS/credentials, write-back) — or
  migrate a connector onto it. Load BEFORE changing agent_connector_sdk/, adding
  an extension port or entry point, or moving a connector off agent-utilities
  imports. Use when the agent must build, fix, review or migrate connector
  code. Covers the module map, the EG generated-contract boundary, the
  wiring and public-API gates, test and gate commands, generated artifacts and
  repo traps. Shared lane, build, gate and landing rules are in
  graphos-ecosystem-development — load it first. Not for engine or agent work.
license: MIT
tags: [agent-connector-sdk, connectors, mcp, manifests, packs, connector-sync, development]
metadata:
  version: '1.3.1'
  author: Genius
---
# agent-connector-sdk development

The SDK is the connector control and transport layer; every connector goes through it.
**Load `graphos-ecosystem-development` first** — isolation, staging, `--no-verify` lane
commits, build hosts, gate caps, landing and decisions are defined there.

## What lives here — and what must not

| Path | Owns |
|---|---|
| `agent_connector_sdk/mcp/` | `create_mcp_server` (in `mcp/server.py`), auth composition, visibility, content, tool surface, subscriptions, registry leases |
| `agent_connector_sdk/manifest/` | manifest models, loaders, sync presets, live-contract validation, fingerprints |
| `agent_connector_sdk/ports/` | one typed protocol per extension boundary |
| `agent_connector_sdk/artifacts/`, `certify/` | MCP content capture, canonical pack construction, certification |
| `agent_connector_sdk/runner/` | the `connector-sync` runner, scheduling, durable EG status reads, health |
| `agent_connector_sdk/sinks/`, `repository/` | the EG sink (commits through generated `SourceIngest`, `ConnectorPack`, `WriteBack`) and repository snapshot transport |
| `agent_connector_sdk/writeback/` | governed dry-run, authorization, version checks, idempotency, reconciliation |
| `http/`, `tls/`, `auth/`, `credentials/` | governed outbound requests, OIDC client credentials, `env://` / `openbao://` references |
| `exceptions.py`, `utilities.py` | `MissingParameterError`, `require_auth`, `to_boolean` for connector code |

Not here: durable graph storage, ontology reasoning, schemas or receipts (EG), agents,
model calls, workflow orchestration (AU), deployment policy (graph-os), vendor API
implementations (each connector). **`agent-utilities` is never a dependency** — the
`phase-direction` gate enforces the direction.

## Rules specific to this repo

- **Import EG-owned schemas from its generated client surface.** Never duplicate a wire
  DTO, digest or method list.
- **Every module reachable, every public name tested.** The public surface is declared in
  `pyproject.toml` `[tool.agent_connector_sdk.wiring]`; `check-orphan-modules` and
  `check-public-api-tested` refuse the rest. Add the entry point AND a discovery test for
  entry-point features.
- **Fail closed** on unknown auth, unsafe network exposure, malformed records, unverified
  tool contracts, uncertified extensions, literal credentials and uncertain write-back
  effects. Secrets stay references; never serialize a resolved value.
- **Async paths stay non-blocking**; bounded blocking work goes behind
  `mcp/concurrency.run_blocking`.
- Connector content (skills, prompts, ontologies, SHACL shapes) is authored in the
  connector, certified here into a digest-pinned pack, and committed by EG `ConnectorPack`.

## Migrating a connector onto the SDK

| agent-utilities import | SDK replacement |
|---|---|
| `create_mcp_server` (AU MCP utilities) | `agent_connector_sdk.mcp.server.create_mcp_server(name, version=…)` → `(args, mcp, middlewares)` |
| `to_boolean` | `agent_connector_sdk.utilities.to_boolean` |
| `MissingParameterError`, `require_auth` | `agent_connector_sdk.exceptions` |
| confirmation / progress context helpers | `agent_connector_sdk.mcp.context` |
| action-routed tool dispatch | `agent_connector_sdk.mcp.action_dispatch` + `mcp.tool_surface.register_tool_surface` |

Delete the AU import in the same change — no aliases. `connector_manifest.yml` is
generated; regenerate it and its certification, never hand-edit.

## Commands

Python-only repository — no cargo. The EG client is consumed from a pinned revision:
release CI checks out EG into `.ci/epistemic-graph`, and
`tests/gates/test_workflow_contract.py` pins the same revision — move both together.

```bash
uv sync
uv run --frozen python -m pytest tests/<the files you touched> -q
uvx --from ruff==0.16.0 ruff check <changed files>
uv run --frozen --with mypy==1.20.2 --with types-PyYAML==6.0.12.20260518 python -m mypy agent_connector_sdk
python scripts/check_wiring.py orphans
python scripts/check_wiring.py public-api
```

The full suite (`complexity-staged`, `kiss-staged`, `jscpd-differential`, `phase-direction`,
`docs-build`, `wheel-build`, `ci-gate-replica`, …) is the landing gate; lanes run the
targeted checks above.

## Traps seen here

- A typed-contract change in EG (dict → model) breaks SDK consumers at runtime only; run
  the sink and runner tests after an EG surface change.
- `pre-commit` config lives under `.config/`; pass `-c .config/pre-commit.yaml`.
- Public docs (`docs/`, README, AGENTS.md) must stay synthetic and current-state — the
  `public-surface` and `tracked-privacy` gates refuse machine paths and history language.

## How to apply

1. Load `graphos-ecosystem-development` and confirm the behaviour is shared connector
   behaviour (SDK) rather than vendor behaviour (connector) or semantics (EG).
2. Add it at one extension port with a typed protocol; declare its public surface.
3. Write positive and adversarial tests, including discovery for entry-point features.
4. Run the targeted checks and the wiring checks above.
5. Commit an explicit allowlist (`--no-verify` only as a coordinated lane) and checkpoint.

Execution: run directly, or delegate through graph-os `graph_orchestrate` with the same
rules. Use an economy model for mechanical connector migrations.
