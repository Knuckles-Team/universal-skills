# US-MCP-BUILDER — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `US-MCP-BUILDER-R001` | `tests/test_mcp_builder_sdk_standard.py::test_http_uses_the_sdk_governed_client_and_pins_no_http_library` | The scaffolded API client imports the governed client and declares no HTTP library. A planted `requests` import, own `httpx` client, retry policy and `requests` pin are each reported. |
| T-002 | `US-MCP-BUILDER-R002` | `tests/test_mcp_builder_sdk_standard.py::test_tls_comes_from_the_resolved_profile` | `auth.py` resolves the profile and no generated module disables verification. Planted bypasses are reported. |
| T-003 | `US-MCP-BUILDER-R003` | `tests/test_mcp_builder_sdk_standard.py::test_secrets_resolve_through_the_sdk` | `auth.py` passes the `*_TOKEN_REF` setting to `bearer_auth`. A planted hand parser and a plain-environment token read are reported. |
| T-004 | `US-MCP-BUILDER-R004` | `tests/test_mcp_builder_sdk_standard.py::test_graphql_uses_the_sdk_extra_and_helpers` | The GraphQL variant depends on `agent-connector-sdk[mcp,graphql]` and imports the SDK helpers. Planted database and `gql` pins are reported. The `vector` extra joins the list when the SDK ships it. |
| T-005 | `US-MCP-BUILDER-R005` | `tests/test_mcp_builder_sdk_standard.py::test_fleet_name_is_declared_once_and_never_spelled` | The entry point, manifest and fingerprints agree and no generated module holds the name. A planted literal binding and a second entry point are reported. `--fleet-name` reaches every declaration. |
| T-006 | `US-MCP-BUILDER-R006` | `tests/test_mcp_builder_sdk_standard.py::test_surface_bootstrap_agent_contract_and_specs` | The scaffold shows each artifact. A planted piped installer and a missing spec file are reported. |
| T-007 | `US-MCP-BUILDER-R007` | `tests/test_mcp_builder_sdk_standard.py::test_version_is_single_sourced_and_bumpversion_tracks_every_pin` | A planted missing file entry, a drifted image pin and a second `__version__` are each reported. |
| T-008 | `US-MCP-BUILDER-R008` | `tests/test_mcp_builder_sdk_standard.py::test_precommit_enables_the_strict_hooks` | The config enables `connector-name --strict`, carries the pending `sdk-conformance` strict entry and a plain `check-cli-help`. The flag renders the live entry. A removed hook and a `uv run` entry are reported. |
| T-009 | `US-MCP-BUILDER-R009` | `tests/test_mcp_builder_sdk_standard.py::test_skill_checklist_names_every_rule_and_sdk_row` | The checklist names every `US-MCP-BUILDER` row and the SDK rows. |
| T-010 | `US-MCP-BUILDER-R010` | `tests/test_mcp_builder_sdk_standard.py::test_scaffold_links_the_ontology_to_the_parent_without_a_todo` | The generated ontology imports the parent, and every class extends a core parent class. The contract check reports a missing import, a class without a parent and a TODO. |
| T-011 | `US-MCP-BUILDER-R010` | `tests/test_mcp_builder_sdk_standard.py::test_scaffold_relies_on_sdk_default_resource_declarations` | The scaffold ships no `data_resources.json` and requires SDK 0.3.19. The SDK derivation proposes a mapping for the scaffolded class. |
