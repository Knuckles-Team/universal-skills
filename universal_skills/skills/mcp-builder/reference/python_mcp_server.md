# Python connector server

The executable scaffold is [scripts/scaffold_connector.py](../scripts/scaffold_connector.py).
It writes a package with no server code: `<pkg>/__init__.py` declares
`connector = Connector(api=Api, get_client=get_client, instructions=...)`, and the
SDK `run()` entry (`python -m <pkg>` or the `scion_sdk.cli:serve`
console script) serves it. Read the maintained SDK source
(`scion_sdk/connector.py`, `mcp/tool_surface.py`) before extending it.

## What the connector holds

- `<pkg>/api_client.py`: class `Api`, one public method per API operation. The
  HTTP verb in the method docstring (`GET /items/{id}: ...`) sets the risk class.
- `<pkg>/auth.py`: `client_factory(url_env=, auth=, tls=, delegation=)` from
  `scion_sdk.auth.declare`, with one of `Bearer`, `ApiKey`, `Basic`,
  `ClientCredentials`, `RefreshToken`, `SessionLogin`, `NoAuth`.
- `<pkg>/connector_sources.py`: `SOURCES` as `source_meta(tool=...)` data;
  the SDK builds the declaration with `load_declaration`.
- `<pkg>/prompts/`, `skills/`, `ontology/`: served by convention.
- Extra tools that are not client methods: a `<pkg>/tools.py` with
  `register_<tag>_tools(mcp)` functions, found by default.

## Version

`pyproject.toml` holds the only version. Read it with `importlib.metadata`.
