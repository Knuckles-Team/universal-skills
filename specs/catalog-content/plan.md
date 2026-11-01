# US-CONTENT — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

The SDK finds content by convention and serves `skills/<name>/SKILL.md`. This package adds no server code. Pinned upstream sources vendor skills with provenance. Two skills carry their own rows: `code-enhancer` and `spec-row-delivery`.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: `agent-connector-sdk[mcp]`
- **Storage**: N/A
- **Testing**: pytest unit tests; the SDK pytest plugin conformance checks
- **Target Platform**: Linux, served by arbora
- **Project Type**: content library
- **Performance Goals**: N/A
- **Constraints**: no server code; no executed upstream file; skills stay atomic and portable
- **Scale/Scope**: about 250 skills

## Constitution Check

- **R-I. A skill is atomic and portable**: pass. The new skill does one job and carries portable frontmatter.
- **Organization article XXIV, complete rows**: pass. Each new row names its file, test and caller chain.

## Project Structure

```text
pyproject.toml                                         existing
upstream-sources.toml                                  existing
scripts/sync_upstream_skills.py                        existing
universal_skills/skills/<name>/SKILL.md                existing
universal_skills/skills/spec-row-delivery/SKILL.md     new
tests/test_catalog_content.py                          existing
tests/test_spec_row_delivery_skill.py                  new
```

## Phase 0: Research

No unknowns; no research.md.

## Phase 1: Design

### Existing system and reuse

The SDK serves `skills/<name>/SKILL.md` through the skills directory provider. The pytest plugin generates the conformance checks.

### Upstream skill sources

`upstream-sources.toml` pins each source at a full commit SHA. `scripts/sync_upstream_skills.py` fetches the pin into a throwaway git repository and reads blobs with `cat-file`. It never runs them. It stores a snapshot in `universal_skills/upstream/<source>/` and renders each skill. It merges `universal_skills/overlays/<name>/*.md` after the render. The pre-commit hook runs `--check` offline, so a hand edit to a vendored file fails the commit.

### Delivery skill

`spec-row-delivery` holds the procedure that one delivery assignment run follows. Meristem loads it through arbora. The skill states the steps, the six report states and the review-thread rules. It forbids a merge, an auto-merge arming, a spec edit and a skipped gate. The engine and arbora enforce those rules too; the skill only guides the model.

### Decisions

Hard cutover: the nested category layout and the `agent_utilities.skill_providers` entry point are gone. A skill's category is its metadata, not a directory.

## Phase 2: Task approach

Tasks follow the rows, producer first. Rows R004.1 to R004.3 run in order.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks must pass, including `check-atomicity`, `check-frontmatter-portability`, `skill-catalog-structure` and `security-sanitizer`. `uv run pytest tests/test_catalog_content.py tests/test_spec_row_delivery_skill.py` must pass.

## Production caller chain

Arbora resolves the installed distribution through the `agent_connector_sdk.connector` entry point. The SDK builds the server and lists each skill resource. A delivery assignment run of meristem reads `skill://spec-row-delivery/SKILL.md` through arbora. No obsolete path exists to delete.

## Cross-repo seams

- `SCION-CONNECTOR-CONTROL-R071.1` (scion-sdk): the content convention that serves the catalog. Contract: `contracts/content-convention.md`.
- `MERISTEM-SCM-R011` (meristem): the run that loads the delivery skill. Contract: `contracts/delivery-skill.md`.
