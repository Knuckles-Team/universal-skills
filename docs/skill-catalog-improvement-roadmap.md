# Skill Catalog Improvement Roadmap

## Purpose and decisions

This roadmap turns the catalog audit into a migration plan. It applies to canonical
`SKILL.md` entries under `universal_skills/`; bundled examples and templates under a
skill's `assets/` directory are not catalog entries.

The governing decisions are:

1. Keep an atomic skill to one trigger, one purpose, and one primary capability.
2. Keep a workflow to a pure dependency graph over atomic skills or one exact MCP
   tool per node. Input/output wiring is allowed; business logic is not.
3. Put provider-, platform-, or package-specific operations in the owning package
   under `agent-packages/agents/<package>/<module>/skills/` and expose them through
   `agent_utilities.skill_providers`.
4. Let universal workflows depend on package-owned skills by exact name and declare
   the owning distribution in `requires`.
5. Separate read-only assessment, proposed change, approved mutation, and
   post-change verification. Financial orders, publication, infrastructure changes,
   identity changes, and other externally visible actions require an explicit gate.
6. Add a category only when it has a clear boundary and at least two independently
   triggerable capabilities; do not create categories merely to hold one workflow.

This document distinguishes completed examples from recommendations. Anything marked
**proposed** remains backlog until its files, tests, package metadata, and migration
are complete.

## Dated audit baseline

The following is the frozen **2026-07-13 pre-remediation baseline**, not a live
catalog count. Update it only by rerunning the catalog auditor against a named commit.

- 263 canonical entries: 98 atomic skills and 165 workflows across 21 categories.
- 59 workflows consisted entirely of generated step placeholders.
- 191 descriptions lacked an explicit trigger phrase; 66 workflows used the same
  engine-oriented generic description.
- 32 workflows reused component identifiers, 131 had frontmatter/team-file role
  drift, and 30 had description/execution-mode drift.
- 24 local documentation links were unresolved.
- The built wheel contained no `SKILL.md` files even though source-tree discovery
  worked.

The baseline scanner is structural. Its findings identify review work; they do not
by themselves prove that a capability is semantically correct or safe.

## Systemic findings and policy

| Finding | Decision | Required remediation |
|---|---|---|
| Atomic skills that contain orchestration | Split reusable operations into atomic skills; move ordering into a workflow. | Remove cross-skill DAGs, workflow metadata, and multi-capability trigger surfaces from atomics. |
| Workflows with inline implementation logic | Treat the workflow as wiring only. | Replace each step with an exact `[skill: name]` or `[mcp_tool: name]` binding and dependency declaration. |
| Generic routing descriptions | Route on user intent, inputs, boundaries, and exclusions. | Add a self-sufficient “Use when…” description and remove engine marketing language. |
| Invalid DAGs or team drift | Make the step graph the source of truth. | Require unique node IDs, resolvable dependencies, an acyclic graph, matching `team.yaml`, rendered execution waves, and the delegation footer. |
| Hollow generated workflows | Do not preserve names without capability. | Delete placeholders; recreate a workflow only after its atomic dependencies exist. |
| Unsafe mutation paths | Default to inspection and preview. | Add explicit authorization, dry-run/idempotency behavior, blast-radius reporting, and verification nodes before allowing mutation. |
| Package-specific operations in the universal catalog | Move the implementation to its owner. | Ship the skill and its resources in the package wheel, register its provider entry point, and leave only portable compositions here. |
| Broken links, missing resources, or untested scripts | Treat instructions and executable assets as one product. | Resolve every local link, run script smoke tests, test failure paths, and remove capabilities the shipped resources do not support. |
| Incomplete wheel contents | Test the installed artifact, not only the checkout. | Assert that wheel discovery includes every canonical `SKILL.md` and required resource while excluding caches and build artifacts. |
| Outdated scaffolders | Make the correct shape the default. | Builders must generate current paths, metadata, trigger descriptions, pure DAG syntax, matching teams, and no placeholder resource trees. |
| Stale catalog documentation | Generate inventory from source metadata. | Keep narrative guidance hand-authored, but derive names, domains, types, and versions from the catalog auditor. |

## Category-by-category decisions

Every current top-level category is covered below. “Refine” means retain the category
while reviewing each member; it does not mean every listed change is complete.

| Current category | Decision and next action |
|---|---|
| `agent-tools` | Refine. Keep reusable agent construction, evaluation, and catalog tooling universal. Split builder/orchestrator hybrids, validate generated output, and keep provider adapters in their packages. |
| `content` | **Added in this change.** Establish the portable editorial boundary around outlining, drafting, copy editing, and publication preflight. Add channel-neutral atomics here; keep actual posting in provider packages. |
| `core` | Refine. Reserve for installation, skill authoring, handoff, and other fleet-wide primitives. Convert any lifecycle-shaped capability into atomics plus a workflow and remove obsolete path guidance. |
| `creative` | Refine. Separate ideation, prompt construction, media transformation, and asset review. Add rights, attribution, reference-image, and user-approval boundaries without embedding publishing. |
| `data` | **Added in this change.** Establish portable dataset profiling, quality validation, and dictionary generation. Keep storage engines, warehouses, and vendor connectors package-owned. |
| `data-workflows` | **Added in this change.** Keep dataset-readiness composition read-only, pass a reviewed rule set and owner notes explicitly, and never infer authorization to ingest or repair data. |
| `development` | Refine. Keep SDD phases, repository analysis, testing, and implementation operations atomic. Improve trigger descriptions and split skills that combine planning, changes, and verification. |
| `development-workflows` | Migrate to pure DAGs. Use `sdd-full-lifecycle` as the target shape, then repair role drift, duplicate nodes, and inline code-generation logic in the remaining workflows. |
| `docs` | Refine. Keep file-format operations and document transformations atomic, verify every referenced script/template, and separate content authorship from format conversion. |
| `finance` | Refine with high-stakes controls. Separate data ingestion, hypothesis evaluation, backtesting, paper execution, and live execution; make assumptions, staleness, and non-advice boundaries explicit. |
| `finance-workflows` | Prioritize migration. Rebuild only from verified finance/research atomics or package-owned exchange/broker skills. Require approval immediately before any live order and verify fills independently. |
| `health-workflows` | Constrain and reassess. The remaining wellness workflows need evidence, scope, escalation, and non-diagnostic boundaries. Add a universal `health` category only after safe atomic capabilities are defined. |
| `infrastructure` | Refine. Keep portable host, network, container, secret, and deployment primitives; distinguish inspection from mutation and relocate vendor-specific operations to owners. |
| `infrastructure-workflows` | Prioritize safety and ownership. Compose portable checks with package-owned operations, declare `requires`, insert approval before mutation, and make post-change verification mandatory. |
| `machine-learning-workflows` | Block expansion until atomics exist. Decompose model training into data, split, train, evaluate, register, and documentation capabilities under a new `machine-learning` category. |
| `ops` | Expand carefully with portable primitives such as intake normalization and change-risk assessment. Ticketing, storage, payroll, and messaging APIs remain package-owned. |
| `ops-workflows` | Rebuild around owning packages. Declare ServiceNow, Atlassian, Nextcloud, Postiz, and similar dependencies explicitly; add privacy, approval, and audit gates for HR/legal/financial flows. |
| `product` | Refine. Keep research, strategy, and risk-analysis outputs distinct. Convert the multi-agent pre-mortem lifecycle into atomics plus a workflow if it retains parallel orchestration. |
| `research` | Refine. Preserve clear search/fetch/crawl/analyze/citation boundaries, fix executable and reference defects, and require provenance, freshness, and source-quality reporting. |
| `research-workflows` | Migrate to pure evidence DAGs. Use package-owned ScholarX operations where applicable and place citation audit before downstream synthesis or publication. |
| `social-workflows` | Narrow to portable compositions. The rebuilt blog workflow is an example; posting, scheduling, analytics, and account operations belong to owning packages and require explicit publication approval. |
| `system` | Refine. Favor read-only host/process inspection and capability discovery. Verify that every claimed utility is shipped and gate commands that kill processes or alter system state. |
| `system-workflows` | Refine the small surface. Keep capability discovery as composition over atomic inspection skills; do not turn it into an unbounded autonomous remediation loop. |
| `web-development` | Refine. Separate design, browser inspection, implementation, accessibility, and visual verification. Add authorization and data-handling limits to cloning/crawling capabilities and consolidate browser overlap. |

## Ownership and relocation rule

A capability is package-owned when its primary trigger names a provider, product,
protocol implementation, or package-specific data model. Examples include ScholarX,
Langfuse, ServiceNow, Portainer, qBittorrent, Nextcloud, Postiz, Owncast, Mealie, Wger,
and exchange-specific trading APIs.

For each relocation:

1. Place the skill at
   `agent-packages/agents/<package>/<module>/skills/<skill-name>/SKILL.md` with its
   scripts, references, and assets.
2. Expose `<module>.skills` through the package's
   `agent_utilities.skill_providers` entry point and include the resources in its
   wheel.
3. Add installation/discovery tests against the built wheel.
4. Change universal workflows to bind the package skill by exact name and list the
   distribution in `requires`.
5. Remove the universal duplicate only after consumers resolve the package provider;
   provide an alias or migration note if a public skill name changes.

A portable workflow may still coordinate several package skills. Portability belongs
in the composition; provider schemas, credentials, retries, and mutations belong in
the owning packages.

## Prioritized category candidates

These are proposals, ordered by risk reduction and reuse. Creating the directory is
not the first step; define and test the atomics first.

| Priority | Proposed category | Minimum useful atomic set | Decision gate |
|---|---|---|---|
| P0 | `security` / `security-workflows` | secret exposure auditor, dependency risk auditor, configuration hardening assessor, remediation verifier | Clear read-only defaults, severity model, and approval boundary. |
| P0 | `observability` / `observability-workflows` | telemetry snapshot, signal correlator, SLO evaluator, incident evidence packager | Vendor-neutral inputs and evidence-backed outputs. |
| P1 | `content-workflows` | Uses the new content atomics and research gates | Move channel-neutral editorial workflows here; leave publishing adapters package-owned. |
| P1 | `machine-learning` | dataset splitter, training-config validator, model trainer, model evaluator, model-card builder | Rebuild `train-model` only after these atomics exist. |
| P1 | `identity-access` | access inventory, entitlement diff, policy evaluator, change verifier | Strong tenant scoping, least privilege, approval, and rollback evidence. |
| P1 | `quality-engineering` | test-plan builder, coverage analyzer, flaky-test detector, release gate | Avoid duplicating development test execution; focus on independent quality decisions. |
| P2 | `accessibility` | document accessibility auditor, web accessibility auditor, remediation verifier | Standards version and evidence must be explicit. |
| P2 | `legal` and `people-ops` | intake/checklist/report atomics only | Require domain review, privacy controls, jurisdiction/context fields, and no autonomous decisions. |
| P2 | `mobile` | mobile project inspector, build/test runner, store-readiness auditor | Add only when platform-neutral contracts can be separated from Apple/Google package operations. |
| P2 | `health` | evidence checker, wellness-plan constraint auditor, escalation gate | Medical safety review is mandatory before introducing diagnostic or treatment-facing capabilities. |

## Pure-DAG workflow designs

Legend: **E** = existing universal atomic skill, **X** = existing package-owned skill,
**P** = proposed atomic skill. A proposed workflow is not implemented merely because
its design appears here.

| Workflow | Status | Pure DAG |
|---|---|---|
| Sourced blog post | Existing, rebuilt example | `web-search` **E** → `content-outline-builder` **E** → `content-draft-writer` **E** → `citation-auditor` **E** → `copy-editor` **E** → `publication-preflight` **E** |
| Academic alpha scanner | Existing, rebuilt example | `scholarx-operations` **X** → `citation-auditor` **E** → `factor-hypothesis-extractor` **E** → `quant-data-ingest` **E** → `qlib-backtester` **E** |
| SDD full lifecycle | Existing, rebuilt example | `spec-intake-wizard` **E** → `spec-generator` **E** → `spec-verifier` **E** → `task-planner` **E** → `sdd-implementer` **E** → `automated-test-runner` **E** |
| Dataset readiness assessment | Existing, added example | `dataset-profiler` **E** → (`data-quality-auditor` **E** ∥ `data-dictionary-builder` **E**) |
| Evidence-backed research brief | Proposed | `web-search` **E** → `web-fetch` **E** → `citation-auditor` **E** → `content-outline-builder` **E** → `content-draft-writer` **E** → `copy-editor` **E** → `publication-preflight` **E** |
| Safe service remediation | Proposed | `telemetry-snapshot` **P** → `incident-classifier` **P** → `remediation-plan-validator` **P** → `change-approval-gate` **P** → `package-service-operations` **X** → `remediation-verifier` **P** |
| Accessible content release | Proposed | `citation-auditor` **E** → `copy-editor` **E** → (`accessibility-auditor` **P** ∥ `rights-and-privacy-auditor` **P**) → `publication-preflight` **E** → `publication-approval-gate` **P** → `package-publisher-operations` **X** |
| Governed model training | Proposed | `dataset-profiler` **E** → `data-quality-auditor` **E** → `dataset-splitter` **P** → `training-config-validator` **P** → `model-trainer` **P** → (`model-evaluator` **P** ∥ `model-card-builder` **P**) → `model-registration-gate` **P** |

Each workflow must use unique nodes. If the same atomic operation is needed twice,
create two uniquely named workflow nodes that both bind the same skill only after the
workflow compiler supports explicit node IDs separate from skill bindings.

## Phased backlog

### Phase 0 — Establish trustworthy inventory

- Keep the catalog auditor and its per-skill report reproducible from a named commit.
- Fix wheel resource inclusion and test installed discovery.
- Correct the atomic and workflow scaffolders before generating more entries.
- Remove or quarantine placeholder-only workflows rather than treating them as
  supported capabilities.

### Phase 1 — Correctness and safety

- Resolve broken local links and script failures.
- Repair invalid dependencies, duplicate workflow nodes, team drift, and execution
  mode drift.
- Review mutation-capable finance, infrastructure, identity, publication, HR, and
  legal workflows for approval, idempotency, rollback, and verification.
- Add focused tests for every changed executable asset and high-risk failure path.

### Phase 2 — Atomicity and ownership migration

- Split workflow-shaped atomics and replace inline workflow logic with exact skill
  bindings.
- Relocate provider-specific operations to owning packages and add provider entry
  points plus wheel tests.
- Deprecate duplicates only after compatibility and consumer discovery are verified.

### Phase 3 — Fill high-value gaps

- Extend the tested `content` and `data` atomics only where new trigger surfaces are
  independently useful; keep their existing example workflows pure.
- Build security and observability atomics before their workflow catalogs.
- Create machine-learning atomics and then replace the monolithic training workflow.
- Add identity/access and quality-engineering only after boundaries with existing
  infrastructure/development skills are documented.

### Phase 4 — Continuous governance

- Run atomicity, catalog, link, workflow compiler, package wheel, and installer tests
  in CI.
- Generate catalog inventory documentation from frontmatter.
- Record deprecations, ownership, and replacement skill names in machine-readable
  metadata.
- Re-audit descriptions, scripts, safety contracts, and dependencies on a scheduled
  cadence.

## Acceptance criteria

An improvement is complete only when the applicable criteria pass.

### Atomic skill

- Kebab-case `name` matches its directory; `domain`, `skill_type: skill`, license,
  version, and trigger-oriented description are present.
- The skill has one capability and no cross-skill DAG, team configuration, hidden
  persistence, or unrelated mutation.
- Inputs, outputs, failure behavior, redaction, and safety boundaries are explicit.
- Every referenced file exists; executable assets have success and failure tests.

### Workflow

- Every node has one exact atomic-skill or MCP binding and contains only wiring.
- Node identifiers are unique; dependencies resolve; the graph is acyclic.
- `team_config` and `references/team.yaml` agree, and `requires` names every external
  package dependency.
- `## Execution` accurately renders dependency waves and ends with the standard
  graph-os/native delegation footer.
- Mutations follow assessment → approval → execution → independent verification.

### Package-owned skill

- The owning package exposes a skill-provider entry point and includes all skill
  resources in its built wheel.
- Installation discovers the skill from the wheel without relying on the source
  checkout.
- Universal duplicates are removed or deprecated with a tested migration path.

### Repository and category

- The changed entries are clean in the catalog auditor and atomicity gate.
- Workflow compilation, local-link checks, relevant script tests, version parity,
  wheel-content tests, and installer validation pass.
- A new category has a documented boundary, at least two independently useful
  atomics, a maintainer/owner, and no unexplained overlap with an existing category.
- Documentation states what remains proposed; release notes do not describe backlog
  items as shipped capabilities.
