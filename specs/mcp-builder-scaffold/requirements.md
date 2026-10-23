# US-MCP-BUILDER-SCAFFOLD — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A child row `.n` is one five-minute unit of work. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `US-MCP-BUILDER-SCAFFOLD-R001` | **Scaffold declares the fleet name.** `scaffold_package.py` declares the console script name as the single `agent_connector_sdk.connector` entry point. The generated manifest and fingerprints carry that name. The generated server uses `ConnectorContent.for_package`. The generated ingest uses `IngestBinding.for_package`. The generated schema script reads the name from the manifest. | `tests/test_mcp_builder_fleet_name.py::test_scaffold_names_the_connector_by_its_fleet_name` finds the fleet name in each generated place and no package-name literal. |
