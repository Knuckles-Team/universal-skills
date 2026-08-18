# Documentation Standard vNext

This is the hybrid documentation contract for an agent package. It keeps the
semantic layer (Concept IDs, ontology, `AGENTS.md`, and source Markdown) as the
authoritative meaning and adds a bounded delivery/discovery layer for agents.
The delivery layer is generated from explicit inputs; it is not a runtime
capability oracle and never replaces the semantic layer.

## Applicability and maturity

Each package may publish `docs/agent-readiness.json`, validated by
`scripts/agent_readiness_schema.json`. It must explicitly label applicability
for content, discoverability, access policy, capabilities, errors, provenance,
measurement, and deployment. A `false` value is a deliberate “not applicable”
decision, not an implied omission.

Every maturity entry has an identifier, one of these kinds, and a level:

- `rfc` is a normative external or ecosystem RFC reference.
- `draft` is a proposed, non-normative standard and cannot be called normative.
- `convention` is a package or ecosystem convention; it is advisory unless an
  operator explicitly promotes it through a reviewed authority.

The generator rejects RFCs that are not normative and rejects unsupported
capability claims. Documentation must not claim an API, MCP, A2A, or skill
surface unless the corresponding applicability evidence is present.
Builder-scaffolded API/MCP/A2A claims use small JSON capability registries that
name the source file being evidenced; the generator validates those files
without importing them. Skill applicability names a real, non-symlinked skill
directory containing `SKILL.md`.

## Source and generated artifacts

`mkdocs.yml` is the exact page-selection authority. The generator reads its
navigation and source Markdown directly. It never imports provider/runtime
modules and never scrapes generated HTML. A release may contain:

- `llms.txt`, a curated, bounded root index;
- `llms-sections/<slug>/llms.txt`, one bounded index per current navigation
  section;
- `llms-full.txt`, only when an operator supplies an explicit context budget;
- `markdown-mirror-manifest.json`, a raw-Markdown source/digest map carrying
  both the canonical negotiated route and an explicit static Markdown fallback
  (`index.md` at the root or `<route>/index.md`); and
- `agent-readiness-manifest.json`, the deterministic applicability, maturity,
  budget, capability, and provenance record.

Only pages currently selected by MkDocs are emitted. Source paths must stay under
the documented root and may not be symlinks, traversal paths, or duplicate URLs.
Generated artifacts are stable JSON/text with sorted manifest keys and SHA-256
digests for the exact inputs. Summaries and full context are bounded before they
are written; oversized or malformed content fails closed. Generation first
builds an in-memory plan and supports a read-only `--check` preview. Files are
published through same-directory atomic replacements only after the complete
plan validates; stale files are pruned only from a prior provenance manifest.
Unowned pre-existing outputs require explicit adoption.

## Access, capability, and privacy policy

Public documentation URLs must use HTTPS and may not contain credentials,
queries, private-network addresses, or private/internal hostnames. Source
Markdown and capability metadata are scanned for secret-like assignments,
bearer values, credential URLs, and private endpoints. Runtime endpoint and
credential references remain operator-owned `AgentConfig` inputs.

Content Signals are an explicit operator value. The only default-safe state is
`policy: unset`; the generator never invents or infers signals. An
`operator-reviewed` policy must carry its reviewed values.

The generator is deterministic and current-only: it does not merge stale pages,
generated HTML, runtime imports, or guessed capabilities into discovery context.
Preview, diff, repository selection, and fleet rollout remain operator/root
responsibilities outside this package-builder contract.
