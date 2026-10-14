---
name: mcp-builder
domain: agent-tools
skill_type: skill
description: >-
  Build or update an MCP connector package using agent-connector-sdk and shared
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

Build one MCP connector package using the maintained SDK scaffold.

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

The canonical scaffold and its assets ship inside this skill; generation requires
no external template repository.

| Backend | Required types | Optional additions |
|---|---|---|
| REST or GraphQL API | `api_client,mcp` | `agent`, `graphql` |
| Local CLI | `cli,mcp` | `agent` |

Every generated package serves MCP. CLI backends need no HTTP base URL or API
credentials. Select exactly one backend; MCP remains the default container entrypoint.

The generator preserves existing project-owned files. Inspect the generated diff
and resolve current authority changes before treating a scaffold as ready.
Optional agent orchestration belongs behind the current agent-utilities runtime
contract; it is not a connector dependency or a second builder.

## Contracts

- Preserve 100% of the supported source operation or command catalog across API
  and MCP surfaces. Require deterministic inventory, schema and dispatch parity;
  distinguish mocked transport coverage from live endpoint checks. Do not replace
  a full integration with placeholder or selected operations.
- Keep vendor requests and pagination in the API client, or subprocess execution
  in the CLI adapter. MCP tools validate inputs and use SDK registration for either
  backend; a local command does not bypass authorization or effect controls.
- Serve declared skills, prompts, ontology, shapes and connector manifest through
  explicit SDK content registration; files in a wheel alone do not prove discovery.
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
Include a negative test rejecting stale agent-utilities connector imports. Run normal
lint and pre-commit gates in an existing environment; report unavailable checks
accurately. Do not install native toolchains or broaden dependencies for unrelated
checks.

For reproducible output, pass `--generation-date YYYY-MM-DD` or set `SOURCE_DATE_EPOCH` (UTC Unix seconds). The explicit date wins; otherwise generation uses today's UTC date. Generation dates never establish delivery or release evidence.
