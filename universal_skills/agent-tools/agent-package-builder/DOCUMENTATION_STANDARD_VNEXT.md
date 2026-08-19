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
  budget, capability, and provenance record;
- `.well-known/api-catalog`, an RFC 9727/RFC 9264 `application/linkset+json`
  linkset emitted only when a validated HTTP-serving authority exists;
- `.well-known/mcp-server-card.json`, an explicitly experimental, versioned
  card emitted only when the bound MCP authority proves HTTP transport support;
  and
- `.well-known/agent-skills.json`, a versioned index of only regular, bound
  `SKILL.md` files.

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
generated HTML, runtime imports, caller-supplied endpoints, or guessed
capabilities into discovery context. Optional RFC 8414 authorization-server and
RFC 9728 protected-resource links require exact, validated `.well-known` JSON
authorities. Libraries and docs-only projects cannot advertise served API/MCP/A2A
surfaces.
Preview, diff, repository selection, and fleet rollout remain operator/root
responsibilities outside this package-builder contract.

## Served-surface TCK

The generated `scripts/agent_readiness_tck.py` is a bounded adapter for a
deployed documentation surface; it does not generate or infer capabilities. A
run must provide an exact allowlisted HTTPS origin. It sends only safe `Accept`
and user-agent headers, never sends authorization, rejects queries, credentials,
private/link-local/loopback destinations, ambient proxies, and redirects. The
explicit `--local-fixture` mode is reserved for deterministic in-process or
loopback fixtures.

The TCK reports structured `agent-readiness-tck/v1` evidence with experimental
maturity and explicit `PASS`, `FAIL`, `UNAVAILABLE`, or `NOT_APPLICABLE` outcomes.
It covers Markdown/HTML negotiation, `Vary: Accept`, cache policy and Link
headers, versioned capability discovery, RFC 9457 JSON/structured-Markdown
metadata parity, denial non-retryability, response/link budgets, and malformed
or stale artifacts. Bodies and secret-bearing headers are never retained; only
bounded metadata and digests enter evidence. A target that cannot be reached or
does not apply is not silently certified.
