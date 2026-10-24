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
  version: '1.4.0'
  author: Genius
---

# MCP Builder

Build one MCP-only connector package on the SDK's components. A connector depends on
`agent-connector-sdk[mcp]>=0.5.1,<0.6` and nothing else from the agent ecosystem: no
agent server, no LLM client, no provider entry points. The connector holds only what
is specific to one external system; the SDK and the shared pipelines own the rest.

Use current main revisions of
[agent-connector-sdk](https://github.com/Knuckles-Team/agent-connector-sdk) and
[pipelines](https://github.com/Knuckles-Team/pipelines) as the authority. Record the
revisions you read.

## Scaffold a connector

    python3 scripts/scaffold_connector.py example-mcp --output-dir /path/to/output

Output is deterministic (no date, user or host name). `scaffold_connector.py` is the
only generator.

    example-mcp/
      pyproject.toml                 name, version (only here), one SDK dependency, one entry point
      README.md   AGENTS.md          connector section + Release section (bump first, tag last)
      .pre-commit-config.yaml        the pipelines reference config (connector-standard, secrets, spec)
      .github/workflows/pipeline.yml       python_pipeline (connector) + container_pipeline (render_connector)
      .github/workflows/connector-pr.yml   shared PR gates
      example_mcp/__init__.py        connector = Connector(api=Api, get_client=get_client, instructions=...)
      example_mcp/__main__.py        from agent_connector_sdk import run; run()
      example_mcp/api_client.py      class Api: one public method per API operation
      example_mcp/auth.py            client_factory(url_env=, auth=, tls=, delegation=)
      example_mcp/connector_sources.py     SOURCES = (source_meta(tool=...), ...)
      example_mcp/prompts/*.json     fastmcp prompts (title, tags, meta)
      example_mcp/skills/<name>/SKILL.md
      example_mcp/ontology/<domain>.ttl    classes extend an EG core class
      specs/README.md  specs/<CONN-ID>/{spec,plan,requirements,tasks,test-spec}.md + status.json
      tests/test_api_client.py       tests of the connector's own client logic only

Nothing else is written. Do not add `mcp_server.py`, `_version.py`, `.bumpversion.cfg`,
`docker/` files, `certification.json`, a shapes file, `mcp_config.json`, `conftest.py`,
`kg_ingest.py` boilerplate or copies of SDK tests: the SDK and pipelines own them, and
everything the connector offers is served over MCP.

## How to build each part

1. **Tools: one per API operation.** Each HTTP method on each endpoint is one public
   method of `Api`; the SDK serves one tool per method, named `<prefix>_<method>`
   (`Connector(tool_prefix=...)` overrides the prefix). The verb in the method docstring
   (`GET /items/{id}: ...`) sets the annotations: GET is read-only, PUT and DELETE are
   idempotent, DELETE is destructive and asks the caller to confirm. Never condense
   operations into `action` or `params_json` dispatch tools. Tools that are not client
   methods go in `<pkg>/tools.py` as `register_<tag>_tools(mcp)`, or in
   `Connector(extra_registrations=...)`. Check the served count against the API
   operation count with `scripts/check_tool_parity.py`.
2. **Data sources: declared data.** `connector_sources.py` holds `SOURCES` built with
   `source_meta(tool=..., source_id=..., record_type=..., id_field=..., ontology_class=...,
   fields={...})`, plus optional `FIELD_SETS` and `SCHEMA_VERSION`. Use `for_each` on a
   source to fan out per parent record. The SDK builds the declaration with
   `load_declaration` and serves it as `connector://resources`. Write no manifest file
   and no `declaration()` function. Set `record_type` to the ontology class name.
3. **Ontology.** `ontology/<domain>.ttl` in the shared `:` namespace. Every class gets
   `rdfs:subClassOf` an epistemic-graph core class (the scaffold uses `:Concept`; narrow
   it when a core class fits) and an object property to a core class. Never
   `owl:imports` the core ontology. Shapes and attestations are generated at release.
   Check with `pipelines-hook connector-ontology-map graph-check`.
4. **Prompts and skills.** Prompts are `prompts/<name>.json`, served as fastmcp prompts
   with title (`identity.role`), tags and `_meta` (role, topic, version, `serves`).
   Skills are `skills/<name>/SKILL.md` directories served by the SDK skills provider.
5. **Use SDK components, never your own.** Auth, TLS, delegation and credential
   rotation: `client_factory` with one declaration (`Bearer`, `ApiKey`, `Basic`,
   `ClientCredentials`, `RefreshToken`, `SessionLogin`, `NoAuth`). Paging:
   `PaginationIterator`. Limits: `RateLimiter`. GraphQL: `GraphQLClient`
   (`agent-connector-sdk[graphql]`). Vector search: the SDK `vector` extra. Optional
   dependencies are SDK extras only. Do not pin `requests`, `httpx` or `gql`.
6. **Server.** The `agent_connector_sdk.connector` entry point
   (`<fleet> = "<pkg>:connector"`) and the console script
   `<fleet> = "agent_connector_sdk.cli:serve"` start the server: health route,
   middleware, transports, content, metadata version. Write no server bootstrap.
7. **Tests.** Write tests of your own client logic only. The SDK pytest plugin
   generates the fleet-name, content, ontology, source, startup and version tests in
   any environment that installs the SDK. Copy none of them; add no `conftest.py`.
8. **Version and release.** The version lives in `pyproject.toml` only; read it with
   `importlib.metadata`. Pipelines bumps it, renders the container files, and
   generates the ontology shapes at build time. The shared workflows publish to PyPI
   and Docker Hub.
   Check a new connector with `connector-name --strict`, the `connector-standard` file
   check and `connector-ontology-map graph-check` before the first push.

## Contracts

- Preserve 100% of the supported source operation catalog across API and MCP surfaces.
  Require deterministic inventory, schema and dispatch parity; distinguish mocked
  transport coverage from live endpoint checks. Do not replace a full integration
  with placeholder or selected operations.
- Keep vendor requests and pagination in the API client. MCP tools validate inputs and
  use SDK registration; they do not bypass authorization or effect controls.
- Use typed SDK ingestion. Source adapters and write-back ports require their
  applicable conformance checks.
- Preserve user scope, authorization and credential-reference boundaries.
  Scaffolding does not authorize external writes, deployment, credential creation,
  publication or changes to live services.
- Keep generated files environment-neutral. Never generate credentials, private
  endpoints, personal identities, a committed .env or a TLS-verification bypass.

## Load the relevant reference

- [Backend contracts](reference/backend_contracts.md): API schemas, authentication,
  pagination and errors; CLI argument vectors, execution bounds and proof cases.
- [Connector contracts](reference/connector_contracts.md): SDK ownership, manifests,
  ingestion/effects, packaging, quality gates and source authorities.
- [Python server](reference/python_mcp_server.md): factory, tools and explicit content.
- [Context helpers](reference/ctx_helpers.md): confirmation, progress and safe logging.
- [File parity](PARITY_MANIFEST.md): the generated tree and who owns every other file.
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
