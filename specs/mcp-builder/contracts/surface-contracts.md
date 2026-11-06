# Contract — surface-contracts

Provider: scion-sdk SCION-CONNECTOR-CONTROL-R915.2
Consumer: universal-skills US-MCP-BUILDER-R011.15

## Wire shape

A connector module `<pkg>/connector_contracts.py` holds four tuples. `CONTRACTS` holds `ToolUseContract(task, steps, description="")`. Each step is `ToolStep(tool, params=(), result=(), refusals=())`, and each refusal is `Refusal(code, when="")`. `LINKS` holds `SurfaceLink(task, tools=(), prompts=(), skills=())`. `LOCATIONS` holds `DataLocation(name, holds, instance, read_tool, store="", route_param="", federation_key="")`. `ROLES` holds `BusinessRole(name, tasks=(), description="")`. The scaffold writes every argument as a literal. The SDK serves the rendered declarations as the connector's `contracts.ttl` ontology resource.

## Refusal codes

The SDK refuses a declaration that names a tool, prompt or skill the server does not serve, a step with no result field, or a location with no held class. The scaffold output raises none of them.

## Authoritative types

[`scion_sdk/surface_contracts.py`](https://github.com/Knuckles-Team/scion-sdk/blob/main/scion_sdk/surface_contracts.py) defines the builders. The template is `CONTRACTS` in [`scaffold_connector.py`](https://github.com/Knuckles-Team/universal-skills/blob/main/universal_skills/skills/mcp-builder/scripts/scaffold_connector.py).

## Test vectors

[`tests/test_mcp_builder_connector_scaffold.py`](https://github.com/Knuckles-Team/universal-skills/blob/main/tests/test_mcp_builder_connector_scaffold.py) holds the generated module the SDK self-check reads.
