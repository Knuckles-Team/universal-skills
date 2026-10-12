---
name: mcp-builder
domain: agent-tools
skill_type: skill
description: >-
  Build or update an MCP connector package using agent-connector-sdk and shared
  pipelines standards. Use for connector scaffolding, API/tool registration,
  package content, ingestion contracts, and release-ready repository structure.
license: MIT
tags: [mcp, development, protocol, tools, api]
metadata:
  version: '1.3.2'
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

The generator preserves existing project-owned files. Inspect the generated diff
and resolve current authority changes before treating a scaffold as ready.
Optional agent orchestration belongs behind the current agent-utilities runtime
contract; it is not a connector dependency or a second builder.

## Contracts

- Keep vendor requests, pagination and authentication in the API client. MCP tools
  validate inputs and call that client through SDK registration.
- Serve declared skills, prompts, ontology, shapes and connector manifest through
  explicit SDK content registration; files in a wheel alone do not prove discovery.
- Use typed SDK ingestion and graph-owned generated contracts. Source adapters
  and write-back ports require their applicable conformance checks.
- Preserve user scope, authorization and credential-reference boundaries.
  Scaffolding does not authorize external writes, deployment, credential creation,
  publication or changes to live services. Required approval and policy gates remain.
- Keep generated files environment-neutral. Never generate credentials, private
  endpoints, personal identities, a committed .env or a TLS-verification bypass.

## Load the relevant reference

- [Connector contracts](reference/connector_contracts.md): SDK ownership, manifests,
  ingestion/effects, packaging, quality gates and source authorities.
- [Python server](reference/python_mcp_server.md): factory, tools and explicit content.
- [Context helpers](reference/ctx_helpers.md): confirmation, progress and safe logging.
- [File parity](PARITY_MANIFEST.md): generated repository and package obligations.
- [Documentation readiness](DOCUMENTATION_STANDARD_VNEXT.md): bounded source-only
  discovery, ownership manifests, public docs and served-surface checks.
- [MCP design](reference/mcp_best_practices.md): tool boundaries and transport choices.
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
