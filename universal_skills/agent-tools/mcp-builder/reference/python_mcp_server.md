# Python connector server

The executable scaffold is [scripts/scaffold_package.py](../scripts/scaffold_package.py).
Verify it against current SDK source before extending a connector.

## Factory and content

    from pathlib import Path

    from agent_connector_sdk.config import load_config
    from agent_connector_sdk.mcp.content import ConnectorContent
    from agent_connector_sdk.mcp.server import create_mcp_server
    from agent_connector_sdk.mcp.tool_surface import register_tool_surface

    from . import __version__, mcp as tools

    def get_mcp_instance():
        load_config()
        package_root = Path(__file__).resolve().parent
        args, server, middlewares = create_mcp_server(
            "Example Connector",
            version=__version__,
            content=ConnectorContent(
                connector="example-connector",
                package_root=package_root,
                package_version=__version__,
                manifest_path=package_root / "connector_manifest.yml",
            ),
        )
        register_tool_surface(server, service="example-connector", tools_module=tools)
        return args, server, middlewares

The factory returns middlewares for the caller to add. Preserve the current
SDK/golden transport runner; stdio logging belongs on stderr. Use stdio or loopback
by default. Network exposure must pass factory authentication and exposure checks.

The content registrar serves skills as skill resources, structured JSON prompts as
native MCP prompts, ontology and SHACL resources, and manifest://connector.
Prompt JSON needs instructions.core_directive. Missing or malformed declared
content must fail, not disappear from discovery. Test actual listed content.

## Condensed tools

Export register_<domain>_tools callables from the package mcp module and pass that
module to register_tool_surface exactly once. The SDK registers condensed tools
with granular and gated tags, honoring domain toggles. There is no selectable
MCP_TOOL_MODE or verbose 1:1 surface. Legacy manifest/client arguments accepted by
the registrar are compatibility no-ops, not an operation exposure mechanism.

Keep tools as thin API adapters with typed, bounded inputs and accurate effect
annotations. SDK action dispatch and policy/authorization boundaries govern effects;
name-based guesses or readOnlyHint alone do not authorize mutations. Test disabled
domains and declared/listed tool agreement.

See [connector contracts](connector_contracts.md) for manifests, ingestion,
packaging and optional agent orchestration.
