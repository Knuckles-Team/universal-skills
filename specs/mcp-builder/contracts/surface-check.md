# Contract — surface-check

Provider: scion-sdk SCION-CONNECTOR-CONTROL-R916.5
Consumer: universal-skills US-MCP-BUILDER-R011.16

## Wire shape

The SDK pytest conformance plugin adds the item `connector_conformance::surface_complete` to any repository that declares a `scion_sdk.connector` entry point. It builds the server, lists its tools, prompts and resources, and checks the `connector_contracts.py` declarations against them.

## Refusal codes

The check fails with one finding per gap: an unserved tool, prompt or skill in a declaration, a missing contract, link or location, or an incomplete prompt agent definition.

## Authoritative types

[`scion_sdk/testing/conformance.py`](https://github.com/Knuckles-Team/scion-sdk/blob/main/scion_sdk/testing/conformance.py) registers the check.

## Test vectors

[`tests/test_mcp_builder_connector_scaffold.py`](https://github.com/Knuckles-Team/universal-skills/blob/main/tests/test_mcp_builder_connector_scaffold.py) runs the check on a generated connector.
