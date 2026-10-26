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
| `.pre-commit-config.yaml` | Pipelines hook reference, including the aggregate connector gate, copied from the shared connector template. Hook implementations and policy remain in pipelines. |
| `.github/spec-dashboard.json`, `.github/workflows/pages.yml`, `pages/index.md` | Connector-owned dashboard source, Pages caller and minimal source page. The reusable Pages workflow and dashboard renderer remain in pipelines; `workflow_dispatch` is retained for an explicit source-bound publish. The caller leaves `shared_theme_enabled` off until the canonical pipelines theme generator has produced and reviewed the required content-tree assets. |
| `.github/workflows/pipeline.yml`, `.github/workflows/connector-pr.yml` | Pipelines release and PR callers. `connector: true` and `render_connector: true` select the shared connector generation paths; the jobs themselves remain in pipelines. |
| `<pkg>/skills/<fleet>-development/SKILL.md` | Connector-owned repository development contract: rapid delivery, setup/gates, connector checks and delivery discipline. |
| Server, health route, transports, version lookup, conformance tests | SDK. |
| Version bump, `docker/*`, shapes, attestation, sanitizer, codespell list | Pipelines, rendered or generated at build or release. |
