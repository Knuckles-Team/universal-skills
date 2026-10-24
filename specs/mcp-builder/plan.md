# US-MCP-BUILDER — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Existing system and reuse

`scripts/scaffold_package.py` and its template modules already generate an SDK-only connector with the governed client, `resolve_tls_profile`, `bearer_auth`, a spec tree and a safe bootstrap. `scripts/check_connector_contract.py` already rejects the retired control-plane package. This spec adds rules to those files and adds no module.

## Architecture

The scaffold writes `pyproject.toml` with the `agent_connector_sdk.connector` entry point and SDK extras, `mcp_server.py` and `kg_ingest.py` with `for_package`, and a pre-commit config with the strict hooks. `check_connector_contract.py` is copied into each generated project and runs the same rules as the `connector-sdk-contract` hook. The skill tests scaffold a demo connector and assert each row.

## Connector scaffold (R011)

`scripts/scaffold_connector.py` writes the minimal tree: `pyproject.toml`, `<pkg>/{tools.py,client.py,__main__.py}`, prompts, skills, ontology, specs, one test file, two workflow callers and the release Dockerfile. The SDK run entry, conformance plugin and metadata version need agent-connector-sdk 0.5.0. `scaffold_package.py` and rows R001 to R010 describe the earlier layout.

## Interfaces and data model

`scaffold(..., fleet_name=)` and `--fleet-name` set the declared name (default `<short>-mcp`). `check_sdk_rules(root, package)` returns findings that end with the violated `US-MCP-BUILDER` row.

## Live integration path

The SDK is read at 0.3.11, which ships `ConnectorContent.for_package`, `IngestBinding.for_package` and the connector entry point group. The SDK has no request limiter, vector extra or GraphQL client class yet; the scaffold adds each when released. The pipelines `sdk-conformance` hook is not published; the scaffold emits it pending.

## Quality and release gates

The repository pre-commit hooks and `tests/test_mcp_builder_sdk_standard.py` must pass. A main push publishes a new skill version.

## Risks, alternatives, and decisions

Alternative: link the rules from `SKILL.md` only. Rejected: prose does not stop a generated connector from drifting, and the audit shows the drift. The static check runs in every generated project instead.
