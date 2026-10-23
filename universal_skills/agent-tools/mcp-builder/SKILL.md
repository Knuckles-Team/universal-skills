---
name: mcp-builder
domain: agent-tools
skill_type: skill
description: >-
  Build or update an SDK-only MCP connector package: it depends on
  agent-connector-sdk alone (never the agent control plane) and follows shared
  pipelines standards. Use when wrapping REST or GraphQL APIs from schemas or
  documentation, exposing a CLI through MCP, or updating connector registration,
  package content, ingestion contracts, and repository scaffolding.
license: MIT
tags: [mcp, development, protocol, tools, api, cli]
metadata:
  version: '1.3.11'
  author: Genius
---

# MCP Builder

Build one MCP-only connector package using the maintained SDK scaffold. A connector
depends on `agent-connector-sdk[mcp]>=0.3.19,<1.0.0` and nothing else from the agent
ecosystem: no agent server, no LLM client, no A2A card, no provider entry points.

Use current main revisions of
[agent-connector-sdk](https://github.com/Knuckles-Team/agent-connector-sdk),
[pipelines](https://github.com/Knuckles-Team/pipelines), and the relevant golden
packages as evidence. Read repository instructions and record exact revisions
before adapting a template. SDK source owns connector APIs; pipelines owns shared
gates and delivery automation. A missing contract in a golden example is not
permission to omit it.

## Scaffold

Run from this skill directory, choosing only the requested package surfaces:

    python3 scripts/scaffold_package.py example-connector --type api_client,mcp --output-dir /path/to/output

The output is an SDK-only package: `pyproject.toml` with the SDK dependency,
`<pkg>/_version.py`, `<pkg>/mcp_server.py` (SDK `create_mcp_server` +
`register_tool_surface` + `ConnectorContent.for_package`), `<pkg>/connector_manifest.yml`,
bundled skills/prompts/ontology, `tests/` using the SDK and an in-process FastMCP
client, and `.github/workflows/pipeline.yml` calling
`Knuckles-Team/pipelines` `python_pipeline.yml@main` with `PYPI_API_TOKEN`.

The canonical scaffold and its assets ship inside this skill; generation requires
no external template repository.

| Backend | Required types | Optional additions |
|---|---|---|
| REST or GraphQL API | `api_client,mcp` | `graphql` (SDK `graphql` extra, no `gql` pin) |
| Local CLI | `cli,mcp` | none |

Every generated package serves MCP. CLI backends need no HTTP base URL or API
credentials. Select exactly one backend; MCP remains the default container entrypoint.

The generator preserves existing project-owned files. Inspect the generated diff
and resolve current authority changes before treating a scaffold as ready.
Pass `--fleet-name <name>` when the fleet name is not `<short>-mcp`; it is declared
once, in the entry point (see the checklist).
There is no agent mode. Orchestration and model calls belong to the agent control
plane, which reaches the connector over MCP.

## Contracts

- **One tool per API operation** is the default build method. Generate one MCP
  tool per method and endpoint (GET, POST, PUT, DELETE...) through the SDK's
  `register_tool_surface(client_cls=..., get_client=...)` or the OpenAPI converter.
  Each tool has a stable snake_case `<prefix>_<operation>` name, a typed input
  schema with required and optional fields, a description from the spec summary or
  docstring, and verb annotations: GET `readOnlyHint=true`, DELETE
  `destructiveHint=true`, PUT and DELETE `idempotentHint=true`, non-GET
  `readOnlyHint=false`. Do not condense operations into `action`-routed or
  `params_json` dispatch tools; a fleet gateway scales the catalog through lazy
  `find` and load. Check the served `tools/list` count against the API operation
  count with `scripts/check_tool_parity.py`.
- **Image standard.** The Dockerfile installs the package from its built wheel or
  from PyPI at an exact version (`pip install --only-binary :all: <pkg>[mcp]==<version>`),
  never from a source copy (`pip install ".[mcp]"`). A dependency that ships only an sdist is
  named in `[tool.pipelines] allow-source-build` (scaffold `--allow-source-build`) and
  exempted by name with `--no-binary <name>`; `check_tool_parity.py` rejects any
  other `--no-binary`. Runtime images build no tools
  from source. Pin the Python 3.14 slim base image by digest and run as a non-root
  user. Tag images `<version>-mcp`.
- Preserve 100% of the supported source operation or command catalog across API
  and MCP surfaces. Require deterministic inventory, schema and dispatch parity;
  distinguish mocked transport coverage from live endpoint checks. Do not replace
  a full integration with placeholder or selected operations.
- Keep vendor requests and pagination in the API client, or subprocess execution
  in the CLI adapter. MCP tools validate inputs and use SDK registration for either
  backend; a local command does not bypass authorization or effect controls.
- Serve declared skills, prompts, ontology, shapes and connector manifest through
  explicit SDK content registration; files in a wheel alone do not prove discovery.
- Ship the connector's OWL/RDF ontology pack from day one. `ontology/<domain>.ttl`
  holds the domain model and reuses core classes by IRI. `ontology/pack.ttl` states
  the connector's own surface and ingest contract as native relationships in the
  engine's connector-pack vocabulary (`cp:`): connector, features, tools, prompts,
  skills, source objects, key rules, cursor, access and provenance policy. Keep
  both in step with the typed declarations; the SDK generates the pack from them
  and the engine imports it, validates it with SHACL and answers selection
  questions over it. Use no blank nodes and no nested property maps.
- Use typed SDK ingestion and graph-owned generated contracts. Source adapters
  and write-back ports require their applicable conformance checks.
- Preserve user scope, authorization and credential-reference boundaries.
  Scaffolding does not authorize external writes, deployment, credential creation,
  publication or changes to live services. Required approval and policy gates remain.
- Include GitHub Pages in authorized public connector publication, using the
  existing generated workflow. Keep private publication private. Verify the
  deployed workflow revision and public documentation URL before claiming delivery.
- Keep generated files environment-neutral. Never generate credentials, private
  endpoints, personal identities, a committed .env or a TLS-verification bypass.

## SDK conformance checklist

A generated connector must meet every rule below on first generation, so new
connectors do not reintroduce the drift the SDK centralization audit found.
`scripts/check_connector_contract.py <root> --package <pkg>` enforces rules 1 to 9
statically and prints the violated `US-MCP-BUILDER` row beside each finding; the
scaffold also runs it as the `connector-sdk-contract` pre-commit hook. The SDK
rows are in agent-connector-sdk `specs/centralized-capabilities/`.

| Rule | Row | SDK row | The connector must |
|---|---|---|---|
| 1 | `US-MCP-BUILDER-R001` | `SDK-CENTRALIZED-CAPABILITIES-R001`, `SDK-CENTRALIZED-CAPABILITIES-R040` | Build every HTTP client with `agent_connector_sdk.http` (`create_http_client`), so SDK retries, 429 handling and egress pinning apply. Pin neither `requests` nor `httpx`; ship no retry loop. |
| 2 | `US-MCP-BUILDER-R002` | `SDK-CENTRALIZED-CAPABILITIES-R008` | Resolve TLS with `resolve_tls_profile`. Never set `verify=False`, silence TLS warnings or build an SSL context. |
| 3 | `US-MCP-BUILDER-R003` | `SDK-CENTRALIZED-CAPABILITIES-R009` | Accept `env://` and `openbao://` references and resolve them through the SDK (`bearer_auth`, `api_key_auth`, the credential resolver). Parse no references by hand and read no token from a plain environment variable. |
| 4 | `US-MCP-BUILDER-R004` | `SDK-CENTRALIZED-CAPABILITIES-R016`, `SDK-CENTRALIZED-CAPABILITIES-R040` | Declare optional dependencies only as SDK extras (`graphql`, `db`, `mssql`, `feeds`, `dataprep`, `market`, `stream`, `integrity`; `vector` once the SDK ships it). For a GraphQL API use the `graphql` extra and the SDK introspection helpers, never a `gql` pin. |
| 5 | `US-MCP-BUILDER-R005` | `SDK-CENTRALIZED-CAPABILITIES-R030` | Declare the fleet name once, as the single `agent_connector_sdk.connector` entry point (SDK-CONNECTOR-CONTROL-R071). Build content with `ConnectorContent.for_package` and ingest with `IngestBinding.for_package`; spell no connector name anywhere else. |
| 6 | `US-MCP-BUILDER-R006` | `SDK-CENTRALIZED-CAPABILITIES-R015` | Ship one tool per API operation with verb hints (reads read-only), the safe `scripts/bootstrap.sh` (no piped installer), the standard `AGENTS.md` agent-contract section, and a `specs/` tree per the pipelines spec standard with tests bound. |
| 7 | `US-MCP-BUILDER-R007` | none | Keep `.bumpversion.cfg` to files that exist, `__version__` in `_version.py` alone, and the Dockerfile image pin tracked by bumpversion at the same version. |
| 8 | `US-MCP-BUILDER-R008` | `SDK-CENTRALIZED-CAPABILITIES-R030` | Enable the pipelines `connector-name` hook with `args: [--strict]`, enable `sdk-conformance` strict, and run `check-cli-help` from a plain install (`python -m <pkg>.mcp_server --help`, no `uv run`, no `find`). |
| 9 | `US-MCP-BUILDER-R010` | `SDK-CONNECTOR-CONTROL-R073`, `SDK-CONNECTOR-CONTROL-R074.7` | Link the domain ontology to the parent: `owl:imports <http://knuckles.team/kg>`, and every class `rdfs:subClassOf` a core class of the parent ontology (the scaffold uses `:Concept`; narrow it to a more specific core class when one fits). Leave no TODO in the ontology. Write no data-resource declarations: the SDK derives them from read-only tools that return records and proposes the ontology mapping by field name. Add `data_resources.json` only to override a default. |

Rule 8 note: pipelines main does not publish `sdk-conformance` yet, so the scaffold
emits it commented out as pending, in strict mode (`SDK_CONFORMANCE_PUBLISHED` in
`scripts/quality_templates.py`). Flip the constant when the hook is published.

The checklist is also the review list: a hand edit that breaks a rule is a defect in
the connector, not a reason to relax the scaffold.

## Load the relevant reference

- [Backend contracts](reference/backend_contracts.md): API schemas, authentication,
  pagination and errors; CLI argument vectors, execution bounds and proof cases.
- [Connector contracts](reference/connector_contracts.md): SDK ownership, manifests,
  ingestion/effects, packaging, quality gates and source authorities.
- [Python server](reference/python_mcp_server.md): factory, tools and explicit content.
- [Context helpers](reference/ctx_helpers.md): confirmation, progress and safe logging.
- [File parity](PARITY_MANIFEST.md): generated repository and package obligations.
- [Documentation readiness](DOCUMENTATION_STANDARD_VNEXT.md): bounded source-only
  discovery, ownership manifests, public docs and served-surface checks.
- [MCP design](reference/mcp_best_practices.md): tool boundaries and transport choices.
- [OpenAPI and publication](reference/openapi_bootstrap.md): provider conversion and
  publishing a validated local tree to a new normal GitHub repository.
- [OpenAPI readiness](reference/openapi_readiness.md): named discovery budgets and
  hash-bound provider evidence; separate from transport and live acceptance.
- [Evaluation](reference/evaluation.md): optional read-only task evaluation with the
  existing model harness; it does not replace static and contract checks.

## Completion evidence

Validate frontmatter and local links, generator rerun behavior and a small isolated
generated project. Check Python syntax, metadata, explicit content/tool registration,
schema/manifest agreement and applicable source/effect contracts without live calls.
Run `scripts/check_connector_contract.py <root> --package <pkg>` (it rejects any
import of, or dependency on, the retired control-plane package). Run normal
lint and pre-commit gates in an existing environment; report unavailable checks
accurately. Do not install native toolchains or broaden dependencies for unrelated
checks.

For reproducible output, pass `--generation-date YYYY-MM-DD` or set `SOURCE_DATE_EPOCH` (UTC Unix seconds). The explicit date wins; otherwise generation uses today's UTC date. Generation dates never establish delivery or release evidence.
