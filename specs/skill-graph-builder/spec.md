# US-SKILL-GRAPH-BUILDER — The builder distills any source into a skill graph

Owner: universal-skills. Cross-repo IDs: `SG-CONTENT-R002`, `SG-CONTENT-R003`, `US-WEB-RESEARCH-R001`, `ARBORA-OPS-R067.1`, `MEDULLA-TYPED-PACKS-R701`.

## Delivery mapping

Component: the `skill-graph-builder` skill.

Depends-on: `US-WEB-RESEARCH-R001`, `SG-CONTENT-R002`.

## User Scenarios & Testing

### User Story 1 - Build a graph from a documentation site (Priority: P1)

A maintainer points the builder at a documentation site and a name. The builder crawls the site through the web-crawler skill and writes a standard graph into the graph collection.

**Acceptance Scenarios**:

1. **Given** a site URL and the name `pandas`, **When** the builder runs, **Then** it writes `pandas-docs` with `SKILL.md`, `index.json`, `sources.json` and a flat `reference/`.
2. **Given** a PDF path, **When** the builder runs, **Then** it classifies the source as `pdf`.

### User Story 2 - Keep a graph traceable (Priority: P1)

A maintainer rebuilds a graph. The new `sources.json` names the builder version, the sources and a digest per file, so the contract gate of `skill-graphs` accepts it.

**Acceptance Scenarios**:

1. **Given** a finished build, **When** the gate runs, **Then** it exits 0.

### User Story 3 - Layer an ontology on a graph (Priority: P2)

A maintainer builds a graph and gets its concept layer as an ontology module whose classes extend the engine core.

**Acceptance Scenarios**:

1. **Given** a build that extracts concepts, **When** it ends, **Then** the module has no orphan class and no `owl:imports`.

### Edge Cases

- A name of 300 characters is shortened with a digest and keeps the `-docs` suffix rule.
- Two pages with one hash prefix get a longer prefix.
- A build without the sibling `skill-graphs` checkout writes to the cache directory.

## Requirements

- **FR-001**: The builder names, classifies, places and flattens a graph. Rows: `US-SKILL-GRAPH-BUILDER-R001`, `US-SKILL-GRAPH-BUILDER-R001.1`, `US-SKILL-GRAPH-BUILDER-R001.2`, `US-SKILL-GRAPH-BUILDER-R001.3`, `US-SKILL-GRAPH-BUILDER-R001.4`.
- **FR-002**: Web sources come from the web-crawler skill only. Rows: `US-SKILL-GRAPH-BUILDER-R002`, `US-SKILL-GRAPH-BUILDER-R002.1`, `US-SKILL-GRAPH-BUILDER-R002.2`.
- **FR-003**: The builder writes provenance and the ontology layer. Rows: `US-SKILL-GRAPH-BUILDER-R003`, `US-SKILL-GRAPH-BUILDER-R003.1`, `US-SKILL-GRAPH-BUILDER-R003.2`.
- **FR-004**: The builder runs without the retired package. Rows: `US-SKILL-GRAPH-BUILDER-R004`, `US-SKILL-GRAPH-BUILDER-R004.1`, `US-SKILL-GRAPH-BUILDER-R004.2`.

## Success Criteria

- **SC-001**: The CLI helper tests pass in a clean environment. Rows: `US-SKILL-GRAPH-BUILDER-R001.3`.
- **SC-002**: A fresh build passes the `skill-graphs` gate. Rows: `US-SKILL-GRAPH-BUILDER-R003.1`.
- **SC-003**: No file under the skill imports `agent_utilities`. Rows: `US-SKILL-GRAPH-BUILDER-R004.1`.

## Assumptions

- The graph format is owned by `SG-CONTENT`. This spec produces it and does not redefine it.
- The `web-crawler` skill stays the single page scraper.

## Why a new spec

A search of `specs/` of this repository found `US-WEB-RESEARCH` for the crawler, `US-MCP-BUILDER` for the connector scaffold and `US-CONTENT` for catalog serving. None owns the `skill-graph-builder` skill. The crawler stays owned by `US-WEB-RESEARCH`; the builder consumes its output. The format rows are in `SG-CONTENT`.

## Scope and interfaces

In scope: the builder CLI, its pipeline package and its output records. Out of scope: the page fetch (`US-WEB-RESEARCH`), the graph format check (`SG-CONTENT`) and the engine import (`MEDULLA-TYPED-PACKS-R700`). Seams: [graph-output](contracts/graph-output.md) and [crawl-source](contracts/crawl-source.md).

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `US-SKILL-GRAPH-BUILDER-R001` | Phase 1: Design | T-001 | |
| FR-002 | `US-SKILL-GRAPH-BUILDER-R002` | Phase 1: Design | T-006 | |
| FR-003 | `US-SKILL-GRAPH-BUILDER-R003` | Phase 1: Design | T-009 | |
| FR-004 | `US-SKILL-GRAPH-BUILDER-R004` | Phase 1: Design | T-012 | |
