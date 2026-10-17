# Python connector server

The executable scaffold is [scripts/scaffold_package.py](../scripts/scaffold_package.py).
Verify it against current SDK source before extending a connector.

## Dependencies and version

The only framework dependency is the SDK; no agent control-plane package, LLM
client or provider entry point belongs in a connector:

    [project]
    dependencies = ["agent-connector-sdk[mcp]>=0.2.1,<1.0.0"]

    [project.scripts]
    example-connector-mcp = "example_connector.mcp_server:mcp_server"

`example_connector/_version.py` holds `__version__ = "0.1.0"` and is the single
version source: `.bumpversion.cfg` rewrites it, `mcp_server.py` imports it.

## Factory and content

    from pathlib import Path

    from agent_connector_sdk.config import load_config
    from agent_connector_sdk.mcp.content import ConnectorContent
    from agent_connector_sdk.mcp.server import create_mcp_server
    from agent_connector_sdk.mcp.tool_surface import register_tool_surface

    from . import mcp as tools
    from ._version import __version__

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

## Manifest, tests and delivery

`connector_manifest.yml` validates against
`agent_connector_sdk.manifest.loader.load_manifest`; with the presets and
`tool_schema_fingerprints.json` under `<pkg>/connectors/` it is checked as a whole
by `require_valid_connector_package`. The scaffold renders the starter manifest
(`render_connector_manifest` in `scripts/connector_templates.py`); regenerate it
instead of hand-editing, and refresh fingerprints with
`python scripts/generate_tool_schemas.py` after any tool signature change.

Generated tests build the server in process (`get_mcp_instance(command_args=[])`),
connect `fastmcp.Client`, and assert listed tools and `manifest://connector`.
Use `agent_connector_sdk.testing` suites for source adapters and write-back.
Certify a running server with `connector-certify . --check -- <command>`.

Delivery is `.github/workflows/pipeline.yml`: the reusable
`Knuckles-Team/pipelines/.github/workflows/python_pipeline.yml@main` with the
`PYPI_API_TOKEN` secret. A merge to main publishes; do not merge without the
release go-ahead.
