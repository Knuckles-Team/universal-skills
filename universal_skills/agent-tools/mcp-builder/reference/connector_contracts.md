# Connector contracts and authority

## Source authority

Record fresh main revisions and read applicable AGENTS.md and .agents/skills
before adapting the scaffold.

| Authority | Owns |
|---|---|
| [agent-connector-sdk](https://github.com/Knuckles-Team/agent-connector-sdk) | Connector server, content, configuration, transport, ingest, source and effect APIs |
| [pipelines](https://github.com/Knuckles-Team/pipelines) | Shared gates, scanner policy, documentation/spec delivery, release and publication |
| [repository-manager](https://github.com/Knuckles-Team/repository-manager) | Repository connector integration examples |
| [servicenow-api](https://github.com/Knuckles-Team/servicenow-api) | Service connector integration examples |

Confirm exact repository identity before using examples. Do not substitute a
similarly named package or unreviewed worktree. Golden packages are evidence,
not permission to copy service-specific state or existing omissions.

## SDK ownership and registration

Connector code imports agent_connector_sdk, not agent_utilities.mcp,
agent_utilities.mcp_utilities or agent_utilities.core connector helpers.
Use load_config, create_mcp_server and register_tool_surface as shown in the
[Python guide](python_mcp_server.md). Explicit ConnectorContent registers declared
skills, prompts, ontology, shapes and connector_manifest.yml.

Verify installed package data and native MCP discovery. Legacy
agent_utilities.*_providers entry points may remain for an existing consumer,
but they do not replace explicit native content registration.

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
agent_connector_sdk.testing.run_source_adapter_suite with fixture sessions and
assert_conformant where applicable.

Write-back needs side-effect-free preview, verified authorization, optimistic
source versions, idempotency and uncertain-outcome reconciliation before retry.
Use run_writeback_suite with an in-memory fixture when adding such a port.
Do not add write-back merely because a provider supports writes.

## Packaging and shared delivery

Depend directly on agent-connector-sdk at a reviewed compatible version. Preserve
its graph-client boundary; do not require epistemic-graph[full] in connectors.
Optional orchestration belongs in its own extra. Avoid recursive extras and
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

The generated scanner workflow prepares its project test environment before
running hooks: `python scripts/bootstrap_environment.py --github`. Commit a valid
`uv.lock` and declare the `test` extra first. The approved runner supplies Python
at the declared minimum version, uv, pre-commit and scanners; the bootstrap does
not download Python or build dependencies. It checks the lock, then performs a
frozen wheel-only sync into ignored `.ci/connector-venv`. Missing wheels or
incompatible lock inputs stop the workflow.

When SDK or EG uses an explicit immutable Git source, the bootstrap verifies the
same full revision in pyproject and lock, checks out clean source, and admits only
that source instead of installing its distribution. Registry dependencies remain
installed normally. The project itself runs from source. Import origins, source
revisions, input hashes and installed distributions are recorded in the private
`.ci/connector-environment.json` receipt. This validates a test environment with
source overlays; it does not certify release wheels or native extension closure.
Hooks use the captured runner pre-commit CLI with the prepared Python first on
PATH, ambient Python import overrides cleared and fleet registration disabled.

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

## Optional agent runtime

Agent orchestration is optional and owned by current agent-utilities runtime.
Verify source/installed entry-point and prompt-schema APIs before exposing the
agent extra. Preserve supported invocation and structured prompts without the
retired standalone agent_data workspace recipe. Connector modules must remain
usable without orchestration dependencies.

## Verification

An isolated smoke test parses generated Python/metadata, inspects tool/content
registration, and validates manifests against authoritative schemas without live
calls. Run applicable source/effect fixture suites and reject stale AU connector
templates explicitly. Report missing environments/checks; do not bypass gates.

New integrations load readiness resources from
universal_skills.agent-tools.mcp-builder.scripts. Consumers of retired paths need
a coordinated source update; this package does not retain compatibility wrappers.
