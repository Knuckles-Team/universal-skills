# Contract — surface-complete

Provider: scion-sdk SCION-CONNECTOR-CONTROL-R916.7
Consumer: universal-skills US-MCP-BUILDER-R011.17

## Wire shape

`scion_sdk.surface_contracts.complete(package) -> str` returns the text of a `connector_contracts.py` module for an installed connector package. The scaffold `complete` mode writes that text when the file is absent and the API is importable. Otherwise it derives the module from the static Api method list.

## Refusal codes

The scaffold treats an import error or a non-string result as "API unavailable" and takes the static path. It never overwrites an existing file.

## Authoritative types

[`scion_sdk/surface_contracts.py`](https://github.com/Knuckles-Team/scion-sdk/blob/main/scion_sdk/surface_contracts.py) defines `complete`. [`scaffold_complete.py`](https://github.com/Knuckles-Team/universal-skills/blob/main/universal_skills/skills/mcp-builder/scripts/scaffold_complete.py) consumes it.

## Test vectors

[`tests/test_mcp_builder_connector_scaffold.py`](https://github.com/Knuckles-Team/universal-skills/blob/main/tests/test_mcp_builder_connector_scaffold.py) completes a fixture connector on the static path.
