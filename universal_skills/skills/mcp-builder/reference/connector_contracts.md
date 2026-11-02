# Connector contracts and authority

## Source authority

Record fresh main revisions and read applicable AGENTS.md and .agents/skills
before adapting the scaffold.

| Authority | Owns |
|---|---|
| [scion-sdk](https://github.com/Knuckles-Team/scion-sdk) | Connector server, content, configuration, transport, ingest, source and effect APIs |
| [pipelines](https://github.com/Knuckles-Team/pipelines) | Shared gates, scanner policy, documentation/spec delivery, release and publication |
| [repository-manager](https://github.com/Knuckles-Team/repository-manager) | Repository connector integration examples |
| [servicenow-api](https://github.com/Knuckles-Team/servicenow-api) | Service connector integration examples |

Confirm exact repository identity before using examples. Do not substitute a
similarly named package or unreviewed worktree. Golden packages are evidence,
not permission to copy service-specific state or existing omissions.

## SDK ownership and registration

Connector code imports scion_sdk only. It is MCP-only: no agent
server, no LLM client and no dependency on the agent control plane.
Declare a `Connector` and start it with the SDK `run()` entry, as shown in the
[Python guide](python_mcp_server.md). The SDK serves the package's skills, prompts,
ontology, shapes and the data-source declaration by convention.

Verify installed package data and native MCP discovery. Explicit ConnectorContent
registration is the only content-discovery path; do not add provider entry points.

## Source and effect contracts

Map provider records into SDK ChangeSet, Entity, Relationship, Document,
MediaAsset and Withdrawal values as applicable, with an explicit IngestBinding.
Use KnowledgeIngest (current_ingest / submit or submit_blocking) and preserve
receipt-checked progress. Do not call retired native_ingest or import an embedded
graph engine.

The manifest declares emitted entity types and relationships. SDK manifest models
and Epistemic Graph generated schemas are authoritative: use their current
generation/validation tools and check freshness. Do not copy request models or
claim undeclared graph capabilities.

Source adapters need deterministic pagination, resumable checkpoints, idempotent
re-runs, malformed-input rejection and complete provenance. Use
scion_sdk.testing.run_source_adapter_suite with fixture sessions and
assert_conformant where applicable.

Write-back needs side-effect-free preview, verified authorization, optimistic
source versions, idempotency and uncertain-outcome reconciliation before retry.
Use run_writeback_suite with an in-memory fixture when adding such a port.
Do not add write-back merely because a provider supports writes.

## Packaging and shared delivery

Depend directly on scion-sdk at a reviewed compatible version. Preserve
its graph-client boundary; do not require epistemic-graph[full] in connectors.
Avoid recursive extras and
import-time live-service initialization.

Current pipelines workflows/hooks own release, publication, Pages, dependency
readiness, spec-delivery docs and public README checks. Under the approved shared
pipeline policy, the generated pre-commit repository and Python/Pages reusable
workflows follow `main`; record the exact resolved revision in validation evidence.
Bundled theme assets retain their immutable provenance and byte checks. Other
dependency and workflow pins remain governed by their own repository policy.
Dependency-readiness is a manual/release gate where current pipelines requires it.

A generated project's resolver lock must come from its reviewed dependency set,
using an existing resolver with native builds disabled where required. Missing
required releases block release/install claims; do not lower dependency bounds or
invent lock entries. If a pipeline policy conflicts with approved immutable pins,
retain the pins and report the conflict until that specific change is authorized.

Retain applicable CCCC complexity, KISS, duplication, architecture and scanner
distribution checks. Reuse shared implementations/profiles rather than another
hand-maintained policy. Provision native tools only through an approved existing
host or CI environment; hooks must not install toolchains. A separately approved
[generated-schema policy](generated_schema_policy.md) may use the shared optional
wrapper; the scaffold never enables exemptions by default.

README is the public entry point; AGENTS records current ownership, commands,
quality gates and isolation. Link detailed specification/delivery evidence from
docs. The current pipelines public-surface gate checks safe local links and README
installation/start paths. Heading, size, badge and privacy conventions need their
own review; a passing public-surface check does not certify them.

## No agent mode

Connectors have no agent mode. Orchestration, routing and model calls belong to
the agent control plane, which reaches a connector only through its MCP surface.
Do not add an agent extra, agent server, A2A card or model client.

## Verification

An isolated smoke test parses generated Python/metadata, inspects tool/content
registration, and validates manifests against authoritative schemas without live
calls. Run applicable source/effect fixture suites and reject any dependency on the
retired control-plane package explicitly. Report missing environments/checks; do not bypass gates.

New integrations load readiness resources from
universal_skills.skills.mcp-builder.scripts. Consumers of retired paths need
a coordinated source update; this package does not retain compatibility wrappers.
