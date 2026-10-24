# US-CONTENT — The catalog is served by the SDK content convention

Owner: universal-skills. Cross-repo IDs: `SDK-CONNECTOR-CONTROL-R071.1`, `SDK-QUALITY-RELEASE-R005.1`.

References: [SDK-CONNECTOR-CONTROL](https://github.com/Knuckles-Team/agent-connector-sdk/tree/main/specs)

## Purpose and user stories

A person installs `universal-skills` next to arbora. arbora serves every skill in it as a native MCP skill resource, with the same declaration every connector uses.

## Requirements and acceptance

The rows are in [requirements.md](requirements.md). The proving tests are in [test-spec.md](test-spec.md).

## Why a new spec

The search covered `specs/` of this repository. The existing specs own published documentation, web research and the mcp-builder scaffold; none owns how the catalog is declared and served.

## Scope and interfaces

In scope: the package layout under `universal_skills/skills/`, the entry-point declaration and the SDK dependency. Out of scope: the content of any single skill.
