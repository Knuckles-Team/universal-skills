# Documentation Standard vNext

RF-ADR-009 section 5 retires `/docs` into GitHub Pages per repository, built
from hand-written sources in `pages/`. A scaffolded connector package follows
that contract directly, publishing through the shared
`Knuckles-Team/pipelines` Pages pipeline rather than a repository-local build.

## Source and generated artifacts

`mkdocs.yml` sets `docs_dir: pages` and is the exact page-selection authority:
`strict: true` and a `nav` naming every page under `pages/` (`index.md`,
`installation.md`, `usage.md`, `deployment.md`, `concepts.md`). It carries
**no** `theme:` or `markdown_extensions:` block — those come from the shared
Pages theme (`templates/mkdocs-theme/base.mkdocs.yml` in `pipelines`),
inherited at build time through mkdocs's native `INHERIT:`, which the
`pages_pipeline.yml` reusable workflow injects for every caller that sets
`shared_theme_enabled: true`. A repository never hand-copies that theme file.

`.github/workflows/pages.yml` is a thin caller of that reusable workflow,
pinned to a full commit SHA, with `content_source: pages`,
`shared_theme_enabled: true`, and `agent_readiness_enabled: true`. It runs no
local `mkdocs build`/deploy steps of its own.

## The agent-readiness delivery layer is generated, by delegation

Enabling `agent_readiness_enabled: true` means the Pages workflow validates
and publishes the canonical agent-discovery layer: `pages/agent-readiness.json`
(the applicability/maturity declaration) against
`pages/agent-readiness.schema.json` (the canonical schema, copied verbatim at
scaffold time — never hand-duplicated), then cross-checks the committed
`llms.txt`, `llms-sections/*/llms.txt`, `markdown-mirror-manifest.json` and
`agent-readiness-manifest.json` (all root-level) against the built site before
deploying (`pipelines/scripts/pages_readiness.py build`, then its `tck`
re-verification).

This package never vendors the ~1,400-line generator that produces those
artifacts. `scripts/generate_agent_readiness.py` is a thin wrapper that
resolves and calls the canonical `universal_skills.agent_readiness.generate()`
authority — the exact same one `repository_manager.docs_readiness` resolves
via `importlib.resources` — from the `docs` dependency group
(`uv sync --group docs`; `universal-skills[agent-package-builder]`, published
to PyPI, is a dev-only dependency of this connector, never a runtime one). Run
it after editing `pages/*.md` or `pages/agent-readiness.json`, then commit its
output.

**`api`/`mcp`/`a2a`/`skills` are all declared `applicable: false`** in the
scaffolded `pages/agent-readiness.json`, even though this package genuinely
serves an MCP tool, ships real skills, and (lane BUILDER-API-CLIENT) now
carries a real outbound vendor API client (`<pkg>/api_client.py`). That last
point does not move this declaration: `capabilities.api` here is RFC
9727/9264 discovery of *this package's own* served surface (a linkset the
generator only emits when the connector serves HTTP — see
`agent_readiness._render_api_catalog`'s `serves_http` gate), never of an API
this connector calls outward. A stdio-default connector serves no such
surface regardless of how many vendor APIs its tools call, so `api.applicable`
tracks `mcp`/`a2a` here, not the presence of an API client:

* the pipelines readiness TCK's own capability validator
  (`pages_readiness._validate_readiness_input`) requires a public HTTPS
  `endpoint` for any `mcp`/`a2a` capability declared `applicable: true`, and
  a stdio-default connector has no such endpoint to prove — set
  `mcp.applicable: true` with a real `endpoint` only once a networked
  deployment exists (see `pages/deployment.md`);
* declaring `skills.applicable: true` (with `discoverability: true`, which
  the Markdown-mirror check requires unconditionally) makes the
  universal-skills generator add `.well-known/agent-skills.json` to its
  `generated` output list, but the pipelines TCK's own output allowlist
  (`GENERATOR_OUTPUTS` in `pages_readiness.py`) does not accept a
  `.well-known/*` path at all — the two canonical validators disagree. This
  is a discovered cross-repo contract gap (`pipelines`, not this builder) to
  raise with whoever owns PAGES-FOUNDATION, not something to route around
  here by hand-editing the shared schema or generator.

## Content discovery is still the native MCP primitive path

Independent of the documentation-site readiness layer above, "what can an
agent discover about this package's MCP surface" is answered by the MCP
server itself:

| Content | Discovered via |
|---|---|
| Tools | `tools/list` |
| Skills | `skill://<name>/SKILL.md` (fastmcp's skills provider) |
| Prompts | `prompts/list` / `prompts/get` |
| Ontology / SHACL shapes | `ontology://<connector>/<file>.ttl`, `shapes://<connector>/<file>.ttl` |
| The connector manifest (sync presets, identity, schema mappings) | `manifest://connector` |

epistemic-graph's pack importer reads the same listings a fleet gateway does
(RF-ADR-009 section 2.1) — there is exactly one channel for that surface, so a
scaffolded package cannot drift between "what its MCP surface documents" and
"what it serves." The Pages readiness layer above is a separate, complementary
concern: discoverability of the *documentation site* by a browsing or crawling
agent, not of the MCP surface.

## Access and privacy policy (unchanged)

Public documentation URLs use HTTPS and never contain credentials, queries,
private-network addresses, or private hostnames. `pages/` source Markdown
must not contain a secret-like assignment, a bearer value, a credential URL,
or a private endpoint — the same rule that governs every other generated
file (`PARITY_MANIFEST.md`'s current-only rejection gate), and the same rule
both `agent_readiness.py` and `pages_readiness.py` scan for independently.
