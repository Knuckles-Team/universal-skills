# Agent Package Builder — Current Parity Manifest

This manifest is the file-by-file contract for a newly scaffolded connector
package. `R` means required; `C` means conditional. RF-ADR-009 (workspace
phase 7, lane BUILDER-RETARGET) retargeted this scaffold: a generated package
depends on **`agent-connector-sdk` and `epistemic-graph` only** — never
`agent-utilities` — builds its MCP server from the SDK's `create_mcp_server`
and `register_tool_surface`, serves its content as **native MCP primitives**
through `ConnectorContent`, declares credentials as `env://`/`openbao://`
references, carries a `connector_manifest.yml` with a valid `sync` preset, and
publishes docs from `pages/` (no `/docs`). Generated files must remain
environment-neutral, current-only, and deterministic.

## Root contract

| Path | Status | Contract |
|---|:---:|---|
| `pyproject.toml` | R | Python 3.12–3.14. `dependencies` is exactly `agent-connector-sdk>=0.1.0,<1.0.0` and `epistemic-graph>=2.23.0,<3.0.0` — never `agent-utilities` or any later workspace-phase package. One console script, `<package>-mcp`. Test deps live in `[dependency-groups] test` (`default-groups = ["test"]`) so `uv sync` installs them without an extra. |
| `.bumpversion.cfg` | R | Version fields in `pyproject.toml`, `README.md` and `docker/Dockerfile` only. |
| `.pre-commit-config.yaml` | R | Reviewed pinned hooks (pre-commit-hooks, ruff, mypy, uv-lock) plus one `repo: https://github.com/Knuckles-Team/pipelines` block with `rev: REPLACE_WITH_SHARED_HOOKS_REV` referencing the shared gate-script bundle by hook id (`complexity-staged`, `kiss-staged`, `clone-dupehound-changed-functions`, `check-secret-history`, `security-sanitizer`, `guardrail-tracked-privacy`, `check-root-hygiene`, `dependency-audit`, `check-orphan-modules`) — RF-ADR-009 section 8's gate-script consolidation. **No gate script is copied into the package**; the block cannot run until the SHARED-HOOKS lane publishes that bundle, and that is expected until it does. Local hooks validate the manifest (`agent_connector_sdk.manifest.loader.require_valid_connector_package`) and run the test suite at pre-push. |
| `.env.example` | R | Non-secret runtime switches (`HOST`, `PORT`, `TRANSPORT`, `AUTH_TYPE`, `MCP_TOOL_MODE`) plus commented `env://`/`openbao://` reference examples for provider credentials. No endpoint, credential, or certificate value. |
| `.env` | — | Must not be generated or committed. |
| `mcp_config.json` | R | Installed stdio entry point and `MCP_TOOL_MODE` only; no resolved reference or raw secret. |
| `README.md` | R | Installation, usage, and the `env://`/`openbao://` credential model; links to the Pages site. |
| `AGENTS.md` | R | Repository ownership table, layout, commands, and the dependency rule (`agent-connector-sdk` + `epistemic-graph` only; never `agent-utilities`). |
| `CLAUDE.md` | R | Stub importing the canonical `AGENTS.md`. |
| `LICENSE` | R | MIT license, `Repository Maintainers`, never a person's identity. |
| `CHANGELOG.md` | R | Keep a Changelog structure. |
| `MANIFEST.in` | R | Includes `connector_manifest.yml`, `skills/`, `prompts/`, `ontology/`, `connectors/` and the package's own Python/JSON/Markdown. |
| `pytest.ini` | R | Unit tests by default; explicit `integration` marker. |
| `.gitignore`, `.gitattributes`, `.dockerignore`, `.codespellignore` | R | Portable repository hygiene; `.env` stays ignored even though it is never generated. |

## Content: served as native MCP primitives (RF-ADR-009 section 2.1)

| Path | Status | Contract |
|---|:---:|---|
| `connector_manifest.yml` | R | A `ConnectorManifest` (`agent_connector_sdk.manifest.model`) at the repository root: `connector`, `resources`, `identity`, `schema_mappings`, one `sync` entry whose `raw` field is the full extraction preset, and `provenance`. Served over MCP as `manifest://connector`. |
| `connectors/mcp_source_presets.json` | R | The same `sync` preset, declared once, cross-checked against the manifest by `agent_connector_sdk.manifest.loader.require_valid_connector_package`. |
| `connectors/tool_schema_fingerprints.json` | R | `{connector, algorithm, tools: {<tool>: <sha256>}}`; the pinned value starts as a placeholder both files share (`PENDING-RUN-scripts/pin_tool_schema.py`), so the manifest/preset/fingerprint cross-check passes immediately while the *live* pin still needs `scripts/pin_tool_schema.py`. |
| `skills/<package>-<domain>/SKILL.md` | R | At least one atomic, provider-prefixed skill, served as `skill://<name>/SKILL.md` (fastmcp's skills provider). |
| `prompts/<package>.json` | R | `{task, description, instructions: {core_directive}, schema_version, source}` — the SDK's `register_connector_content` requires `instructions.core_directive`. Served via `prompts/list`/`prompts/get`. |
| `ontology/<package>.ttl` | R | Out-of-the-box provider ontology only. Served as `ontology://<connector>/<file>.ttl`. |
| `ontology/shapes/<package>.shapes.ttl` | R | SHACL shape for the same class. Served as `shapes://<connector>/<file>.ttl`. |
| `scripts/pin_tool_schema.py` | R | Computes the live tool's compatibility fingerprint (`agent_connector_sdk.manifest.tool_schema`) and writes it into both `connector_manifest.yml` and `connectors/tool_schema_fingerprints.json`. Run once after `uv sync` and whenever the tool's parameters change; `McpToolSourceAdapter.discover()` fails closed on a stale or placeholder pin. |

## Runtime and container contract

| Path | Status | Contract |
|---|:---:|---|
| `docker/Dockerfile` | R | One multi-stage image (no separate agent-runtime target — agent orchestration is a later workspace phase this package must never depend on); loopback default; `AUTH_TYPE` required for a non-loopback listener. |
| `docker/debug.Dockerfile` | R | Development image; no network-to-shell installer. |
| `docker/mcp.compose.yml` | R | Immutable image input, loopback publication, `AUTH_TYPE` required for the networked service. |
| `.github/workflows/ci.yml` | R | `uv sync`, `scripts/pin_tool_schema.py`, `pytest`, ruff, mypy. Does **not** provision or run the shared gate-script bundle — that lands with the SHARED-HOOKS lane and repository-manager's combined gate runner. |
| `.github/workflows/pages.yml` | R | Builds `mkdocs build --strict --site-dir site` from `pages/` and deploys to GitHub Pages (mirrors `agent-connector-sdk`'s own workflow). |

## Documentation contract — `pages/`, not `/docs`

| Path | Status | Contract |
|---|:---:|---|
| `mkdocs.yml` | R | `docs_dir: pages`, Material theme, `strict: true`. |
| `pages/index.md` | R | Package purpose, one line on what it is built on. |
| `pages/installation.md` | R | `uvx`/`pip` install; Python 3.12–3.14. |
| `pages/usage.md` | R | The tool's action-routed contract; how to swap the demo data for real API calls. |
| `pages/deployment.md` | R | Local stdio default; networked deployment requires `AUTH_TYPE` and a loopback-only publish behind an operator-owned authenticated TLS ingress. |
| `pages/concepts.md` | R | Native content primitives, governed sync, credentials by reference. |

There is no `docs/`, no `llms.txt`, no `.well-known/` discovery apparatus, and
no `agent-readiness.json` generation in a scaffolded package — that pipeline
(`scripts/agent_readiness.py` / `agent_readiness_tck.py`, still available as a
standalone tool for repository-manager) is unrelated to RF-ADR-009 and is no
longer wired into this scaffold.

## Python package contract

| Path | Status | Contract |
|---|:---:|---|
| `<pkg>/__init__.py` | R | `__version__` only; no legacy alias. |
| `<pkg>/mcp_server.py` | R | `build_server()` calls `agent_connector_sdk.mcp.server.create_mcp_server` with a `ConnectorContent` pointing at the repository root, then `agent_connector_sdk.mcp.tool_surface.register_tool_surface`. `mcp_server()` (the console-script entry point) passes `host`/`port` only for a non-`stdio` transport. |
| `<pkg>/mcp/__init__.py`, `<pkg>/mcp/mcp_<domain>.py` | R | One action-routed tool (`action` + `params_json`) per domain, exported as `register_<domain>_tools`. |
| `<pkg>/credentials.py` | R | Wires `agent_connector_sdk.credentials`: `build_resolver()` (env, plus OpenBao when `OPENBAO_ADDR` is set) and `resolve_setting()`. No raw secret handling of its own. |

## Tests

| Path | Status | Contract |
|---|:---:|---|
| `tests/servers.py` | R | In-process well-formed and malformed FastMCP servers for the test suite (not collected as tests). |
| `tests/conftest.py` | R | `sessions`, `malformed_sessions`, `repo_root`, `adapter` fixtures, mirroring `agent-connector-sdk`'s own `tests/conftest.py`. |
| `tests/test_manifest.py` | R | `require_valid_connector_package` succeeds against the repository root. |
| `tests/test_mcp_server.py` | R | The in-process server lists the tool, prompt, ontology/shapes/manifest resources and the skill, and the tool call round-trips. |
| `tests/test_credentials.py` | R | `env://` resolution, unset reference, malformed reference, and an unavailable env target — all through `agent_connector_sdk.credentials`. |
| `tests/test_conformance.py` | R | `agent_connector_sdk.testing.source_adapters.run_source_adapter_suite` passes against the manifest's `sync` preset. |

## Current-only rejection gate

A scaffold fails parity if it contains any of the following:

- an `agent-utilities` dependency, import, or entry point of any kind;
- anything other than `agent-connector-sdk` + `epistemic-graph` as runtime
  dependencies;
- a generated `.env`, a raw credential/endpoint value, `SSL_VERIFY`, or a
  `verify=False` path;
- a copied gate script (`check_scanners.py`, `run_kiss.sh`, or any script the
  SHARED-HOOKS bundle is meant to own) inside the package;
- `docs/`, `llms.txt`, or any `.well-known/` discovery artifact;
- an unpinned or empty `sync[].tool_schema_sha256` in `connector_manifest.yml`;
- a person's name, email, real local path, or environment-specific connection
  profile.
