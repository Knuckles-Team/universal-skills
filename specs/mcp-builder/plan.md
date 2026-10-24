# US-MCP-BUILDER — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Existing system and reuse

The SDK owns `Connector`, `run`, `load_declaration`, `client_factory` and the pytest conformance plugin. Pipelines owns the reference pre-commit config, the shared workflows and the `connector-name`, `connector-standard` and `graph-check` gates. This spec adds one generator and reuses all of them.

## Architecture

`scripts/scaffold_connector.py` writes the minimal tree: `pyproject.toml`, `<pkg>/{__init__,__main__,api_client,auth,connector_sources}.py`, prompts, skills, ontology, specs, one test file and two workflow callers. `tests/test_mcp_builder_connector_scaffold.py` generates a connector, installs it into a throwaway environment and runs the SDK, the plugin and the pipelines gates against it.

## Interfaces and data model

`scaffold_connector.py <fleet-name> --output-dir <dir>` writes `<dir>/<fleet-name>`. It never overwrites an existing file.

## Live integration path

The SDK is read at 0.5.1. The core ontology for the graph check is fetched at a revision pinned in the test.

## Quality and release gates

The repository pre-commit hooks and `tests/test_mcp_builder_sdk_standard.py` must pass. A main push publishes a new skill version.

## Risks, alternatives, and decisions

Alternative: link the rules from `SKILL.md` only. Rejected: prose does not stop a generated connector from drifting, and the audit shows the drift. The static check runs in every generated project instead.
