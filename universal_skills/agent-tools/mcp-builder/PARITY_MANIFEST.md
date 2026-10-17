# MCP Builder parity contract

The generator creates a portable connector repository. Required artifacts are
conditional on one backend (`api_client` or `cli`) with mandatory `mcp`. Add
`graphql` for API clients only. Connectors are MCP-only; there is no agent mode. Existing
project-owned files remain unchanged on rerun; review their compatibility instead
of overwriting them. Current SDK and pipelines source remain authoritative.

## Repository files

| Artifact | Contract |
|---|---|
| pyproject.toml, requirements.txt | Direct reviewed agent-connector-sdk dependency; `agent-connector-sdk>=0.2.0,<1.0.0` as the only framework dependency; explicit package discovery/data; no recursive extras or mandatory embedded graph engine. |
| .bumpversion.cfg, LICENSE, CHANGELOG.md | Consistent versions and maintainer metadata; an Unreleased scaffold with a reproducible generation date, never invented release history. |
| README.md, AGENTS.md, CLAUDE.md | Public entry point and current contributor guidance validated by pipelines public-surface; CLAUDE imports AGENTS. |
| .pre-commit-config.yaml | Shared pipelines hooks and lint, test, docs, security, generated-contract and supply-chain checks at reviewed revisions. |
| Scanner policies/wrappers | Applicable complexity, duplication and architecture checks with shared authoritative profile and source-distribution inclusion; no hook-time native installation. |
| .github/workflows | Current reusable pipeline, Pages, scanner, specification-delivery and release/dependency-readiness contracts as applicable, with reviewed immutable sources. |
| Docker and Compose assets | Digest-pinned images, least privilege, stdio/loopback defaults, authenticated TLS for network exposure, read-only operator configuration. |
| mcp_config.json and local examples | Installed entry point and safe switches; no retired MCP_TOOL_MODE, credentials, private deployment addresses or generated .env. |

## Connector implementation

| Artifact | Contract |
|---|---|
| API backend: api/ and auth.py | Provider semantics, bounded HTTP, origin/redirect/TLS protections, SDK configuration and credential references. |
| CLI backend: cli.py | Operator-configured executable, reviewed fixed argument vectors, no shell or ambient credentials, bounded time/output and safe process cleanup. The starter execution boundary is POSIX; discovery remains inert and portable. |
| mcp/ | Condensed tools with bounded schemas, truthful effect declarations and calls to the selected backend. |
| mcp_server.py | SDK load_config, factory, one registrar and explicit ConnectorContent; caller applies returned middleware. |
| connector_manifest.yml | Packaged emitted types/relationships and applicable capabilities, validated by current SDK/graph-owned tooling. |
| skills/, prompts/, ontology/, optional shapes | Portable provider content and native discovery; no deployment-specific ontology; prompt body in instructions.core_directive. |
| kg_ingest.py | SDK typed ChangeSet and IngestBinding submission; no AU native ingestion or embedded graph dependency. |
| Requested source/effect ports | Provenance, checkpoints, receipt validation, deterministic retries; authorized/idempotent effects with preview and reconciliation. |
| _version.py | Single version source read by setuptools-free bump2version and imported by mcp_server.py. |

## Documentation and discovery

Strict MkDocs navigation covers current public documentation, contributor and
specification-delivery evidence, and actual capabilities. See
[documentation readiness](DOCUMENTATION_STANDARD_VNEXT.md) for the detailed contract.

Each generated capability has a six-file spec bundle and an index. Requirement
definitions map to real source/test files; initial status is SPECIFIED with empty
landing and verification receipts. Declare only real prerequisites with Depends-on;
References and Code links do not establish dependency or verification claims.

The site's presentation inherits the unmodified pinned pipelines theme. Its asset
snapshot carries upstream revision and SHA-256 provenance; the upstream sync/check
implementation validates generated assets. Source distributions retain the theme
and spec inputs for offline site builds. The main-push Pages workflow verifies
theme bytes, readiness, and renders source-backed delivery/architecture snapshots.

Preserve the source-only readiness generator/schema, served-surface TCK, explicit
applicability registry, bounded llms indexes, Markdown mirror and provenance
manifests. Full-context and well-known discovery artifacts need explicit budgets
and bound evidence. Never infer live endpoints or availability from source files.

## Checks and rejection cases

Validate generated Python/metadata, entry points, installed data, schema/manifest
agreement, actual tool/content registration, source/effect fixture conformance
and normal repository gates. Test CLI process limits and argument safety with isolated
executables, and API contracts through mock transports. Verify every supported
backend/type combination in wheel and source distributions. Preserve rerun and documentation ownership contracts.

Reject imports or dependencies on the retired control-plane package, and native_ingest; missing content registration;
undeclared ingestion types; retired modes presented as current APIs; recursive
extras or mandatory epistemic-graph[full]; credentials, private endpoints or TLS
bypasses; authorization bypasses or unsafe effect retries; mutable sources where
immutable ones are required; and silent failures presented as certification.
