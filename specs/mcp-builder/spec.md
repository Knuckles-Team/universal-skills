# US-MCP-BUILDER — The mcp-builder scaffold builds connectors on SDK components

Owner: universal-skills. Cross-repo IDs: `SCION-CONNECTOR-CONTROL-R019.1`, `SCION-CONNECTOR-CONTROL-R028.4`, `SCION-QUALITY-RELEASE-R005.1`, `SCION-SOURCE-INGEST-R004.29`.

References: [SCION-CENTRALIZED-CAPABILITIES](https://github.com/Knuckles-Team/scion-sdk/blob/main/specs/centralized-capabilities/spec.md)

## Purpose and user stories

A maintainer runs the `mcp-builder` scaffold to start a connector. The generated connector holds only what is specific to one external system and uses SDK components for the server, tests, version lookup and auth. The shared pipelines own gates, container files and release.

## User scenarios and testing

### User Story 1 - Start a connector from the scaffold (Priority: P1)

A maintainer runs the scaffold for a new external system and gets a connector that holds only what is specific to that system, so that the SDK and pipelines own everything shared.

**Acceptance scenarios**

1. Given a fleet name, When the maintainer runs the scaffold, Then it writes exactly the minimal connector tree and none of the SDK-owned or pipelines-owned files.
2. Given the same fleet name, When the maintainer runs the scaffold twice in clean directories, Then the two trees are byte-identical.
3. Given a file that already exists in the output directory, When the scaffold runs, Then it leaves that file unchanged.

### User Story 2 - Pass the shared gates on the first push (Priority: P1)

A maintainer pushes the generated connector and the shared gates pass without edits.

**Acceptance scenarios**

1. Given a generated connector, When the connector-name and connector-standard gates run, Then they pass.
2. Given the generated ontology, When the ontology graph check runs against the core ontology, Then it raises no finding.
3. Given the generated package, When the SDK conformance plugin runs, Then it passes.

### User Story 3 - Serve one tool per API operation (Priority: P2)

A client of the generated connector sees one MCP tool per API operation with a risk class that follows the verb.

**Acceptance scenarios**

1. Given the generated `Api` class, When the SDK serves it, Then each public method is one tool and none takes an `action` or `params_json` argument.

## Edge Cases

- A fleet name with a trailing `-mcp` or mixed case maps to one package and display name.
- An existing output directory with some generated files keeps those files and writes only the missing ones.
- A generated connector never imports `requests` or `httpx` and never disables TLS verification.

## Assumptions

- The SDK floor is 0.5.1 and the generated dependency stays below 0.6.
- The pipelines gates and the core ontology revision are fetched by the tests and need no local checkout.
- Existing connectors are migrated by their own repositories, not by this scaffold.

## Requirements and acceptance

The rows are in [requirements.md](requirements.md). The proving tests are in [test-spec.md](test-spec.md).

## Why a new spec

The search covered `specs/` of this repository. `US-PAGES` owns published documentation and `US-WEB-RESEARCH` owns the web skills. No spec owns the connector scaffold.

## Scope and interfaces

In scope: `universal_skills/skills/mcp-builder/` (`SKILL.md`, `scripts/scaffold_connector.py`).

Out of scope: the SDK capabilities themselves (SDK owns them), the pipelines hook bodies (pipelines owns them), and migrating existing connectors (each connector repository owns its own fix).
