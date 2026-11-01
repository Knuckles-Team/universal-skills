# US-CONTENT — The catalog is served by the SDK content convention

Owner: universal-skills. Cross-repo IDs: `SCION-CONNECTOR-CONTROL-R071.1`, `SCION-QUALITY-RELEASE-R005.1`, `MERISTEM-SCM-R012`, `MEDULLA-SDLC-R019.7`.

## Delivery mapping

Component: Skill catalog
Depends-on: SCION-CONNECTOR-CONTROL-R071.1
References: [SCION-CONNECTOR-CONTROL](https://github.com/Knuckles-Team/agent-connector-sdk/tree/main/specs)
Code: ../../pyproject.toml ../../scripts/sync_upstream_skills.py ../../tests/test_catalog_content.py

## User Scenarios & Testing

### User Story 1 - Serve the catalog by convention (Priority: P1)

A person installs `universal-skills` next to arbora. Arbora serves every skill as a native MCP skill resource. The package uses the same declaration as every connector.

**Acceptance Scenarios**:

1. **Given** the installed package, **When** arbora builds the server, **Then** it lists one skill resource per skill folder.

### User Story 2 - Vendor skills from pinned upstream sources (Priority: P2)

A maintainer lists an upstream repository and a commit. The catalog gains its skills. One reviewable change moves it to the latest upstream commit.

**Acceptance Scenarios**:

1. **Given** a pinned source, **When** the sync runs, **Then** the skills and their provenance appear, and no upstream file runs.
2. **Given** a hand edit to a vendored file, **When** the offline check runs, **Then** it reports drift.

### User Story 3 - Keep the code-enhancer skill on the constitution (Priority: P3)

A maintainer runs the `code-enhancer` skill. Its limits come from the organization constitution.

**Acceptance Scenarios**:

1. **Given** the skill scripts, **When** the test reads them, **Then** it finds the constitution limits and no baseline mode.

### User Story 4 - Guide one delivery assignment run (Priority: P2)

The platform delivers a spec row as a change proposal. The assignment run loads one skill with the delivery procedure. The run follows it and never merges.

**Acceptance Scenarios**:

1. **Given** the `spec-row-delivery` skill, **When** a delivery assignment run loads it, **Then** it reads the steps in order and the six report states.
2. **Given** the skill text, **When** the validation test reads it, **Then** it finds the prohibitions on merge, arming, spec edits and skipped gates.

### Edge Cases

- A skill outside the flat `skills/<name>/` layout fails the layout test.
- A pin that is not a full commit SHA is rejected.
- A delivery skill text without a prohibition fails its validation test.

## Requirements

- **FR-001**: The package must declare one content-only entry point and serve every skill. Rows: `US-CONTENT-R001`.
- **FR-002**: The catalog must vendor skills from pinned upstream sources with provenance. Rows: `US-CONTENT-R002`.
- **FR-003**: The `code-enhancer` skill must follow the organization constitution. Rows: `US-CONTENT-R003`.
- **FR-004**: The catalog must hold the `spec-row-delivery` skill with the delivery procedure and its prohibitions. Rows: `US-CONTENT-R004`, `US-CONTENT-R004.1`, `US-CONTENT-R004.2`, `US-CONTENT-R004.3`.

## Success Criteria

- **SC-001**: The served skill list equals the skill folders. Rows: `US-CONTENT-R001.3`.
- **SC-002**: The offline check reports every hand edit to a vendored file. Rows: `US-CONTENT-R002.7`.
- **SC-003**: The delivery skill states every step and all four prohibitions. Rows: `US-CONTENT-R004.3`.

## Assumptions

- The SDK content convention serves `skills/<name>/SKILL.md` through the skills directory provider.
- Meristem loads a skill resource for a delivery assignment run through arbora.

## Why a new spec

The search covered `specs/` of this repository. The existing specs own published documentation, web research and the mcp-builder scaffold. None owns how the catalog is declared and served.

## Scope and interfaces

In scope: the package layout under `universal_skills/skills/`, the entry-point declaration and the SDK dependency. The catalog can also hold skills vendored from pinned upstream repositories (`upstream-sources.toml`, `scripts/sync_upstream_skills.py`, `universal_skills/overlays/`). Out of scope: the content of any single skill. Two exceptions apply: the constitution conformance of `code-enhancer` (`US-CONTENT-R003`) and the `spec-row-delivery` procedure (`US-CONTENT-R004`).
