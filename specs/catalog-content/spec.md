# US-CONTENT — The catalog is served by the SDK content convention

Owner: universal-skills. Cross-repo IDs: `SCION-CONNECTOR-CONTROL-R071.1`, `SCION-QUALITY-RELEASE-R005.1`.

References: [SCION-CONNECTOR-CONTROL](https://github.com/Knuckles-Team/agent-connector-sdk/tree/main/specs)

## Purpose and user stories

A maintainer lists an upstream repository and a commit; the catalog gains its skills and moves to upstream's latest with one reviewable change. A person installs `universal-skills` next to arbora. arbora serves every skill in it as a native MCP skill resource, with the same declaration every connector uses.

## Requirements and acceptance

The rows are in [requirements.md](requirements.md). The proving tests are in [test-spec.md](test-spec.md).

## Why a new spec

The search covered `specs/` of this repository. The existing specs own published documentation, web research and the mcp-builder scaffold; none owns how the catalog is declared and served.

## Scope and interfaces

In scope: the package layout under `universal_skills/skills/`, the entry-point declaration and the SDK dependency. The catalog can also hold skills vendored from pinned upstream repositories (`upstream-sources.toml`, `scripts/sync_upstream_skills.py`, `universal_skills/overlays/`). Out of scope: the content of any single skill.
