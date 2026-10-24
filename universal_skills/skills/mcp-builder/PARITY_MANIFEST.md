# MCP Builder parity contract

`scripts/scaffold_connector.py` writes a portable connector repository holding only
connector-specific files. Project-owned files stay unchanged on rerun.

| Artifact | Owner and contract |
|---|---|
| `pyproject.toml` | Connector. The only place the version, the fleet name entry point and the SDK floor are spelled. |
| `<pkg>/__init__.py`, `__main__.py` | Connector. The `Connector` value and the two-line `run()` entry. |
| `<pkg>/api_client.py`, `auth.py` | Connector. One method per operation; one `client_factory` declaration. |
| `<pkg>/connector_sources.py` | Connector. Declared data sources as data. |
| `<pkg>/prompts/`, `skills/`, `ontology/` | Connector content, served by convention over MCP. |
| `specs/`, `README.md`, `AGENTS.md`, `tests/` | Connector. Specs follow the pipelines spec standard. |
| `.pre-commit-config.yaml`, `.github/workflows/*.yml` | Pipelines reference, copied from the shared template. |
| Server, health route, transports, version lookup, conformance tests | SDK. |
| Version bump, `docker/*`, shapes, attestation, sanitizer, codespell list | Pipelines, rendered or generated at build or release. |
