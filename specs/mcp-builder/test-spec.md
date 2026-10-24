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
| T-013 | `US-MCP-BUILDER-R011.1` | `tests/test_mcp_builder_connector_scaffold.py::test_scaffold_emits_exactly_the_minimal_tree` | Minimal tree holds on a generated connector. |
| T-014 | `US-MCP-BUILDER-R011.2` | `tests/test_mcp_builder_connector_scaffold.py::test_generation_is_deterministic` | Deterministic output holds on a generated connector. |
| T-015 | `US-MCP-BUILDER-R011.3` | `tests/test_mcp_builder_connector_scaffold.py::test_identity_and_version_live_in_pyproject_only` | Identity and version in pyproject only holds on a generated connector. |
| T-016 | `US-MCP-BUILDER-R011.4` | `tests/test_mcp_builder_connector_scaffold.py::test_workflows_call_the_shared_pipelines_for_pypi_and_docker` | Shared workflows for release and PR holds on a generated connector. |
| T-017 | `US-MCP-BUILDER-R011.5` | `tests/test_mcp_builder_connector_scaffold.py::test_one_tool_per_operation_with_risk_annotations` | One tool per operation with risk classes holds on a generated connector. |
| T-018 | `US-MCP-BUILDER-R011.6` | `tests/test_mcp_builder_connector_scaffold.py::test_sources_are_declared_in_tool_meta_and_no_manifest_file_exists` | Sources declared in tool metadata holds on a generated connector. |
| T-019 | `US-MCP-BUILDER-R011.7` | `tests/test_mcp_builder_connector_scaffold.py::test_prompt_skill_and_ontology_are_served_over_mcp` | Content served over MCP holds on a generated connector. |
| T-020 | `US-MCP-BUILDER-R011.8` | `tests/test_mcp_builder_connector_scaffold.py::test_ontology_rolls_up_to_a_core_class_and_never_imports_the_parent` | Ontology rolls up to a core class holds on a generated connector. |
| T-021 | `US-MCP-BUILDER-R011.9` | `tests/test_mcp_builder_connector_scaffold.py::test_pipelines_connector_gates_pass` | Pipelines connector gates pass holds on a generated connector. |
| T-022 | `US-MCP-BUILDER-R011.10` | `tests/test_mcp_builder_connector_scaffold.py::test_ontology_graph_check_passes_against_the_core_ontology` | Ontology graph check passes holds on a generated connector. |
| T-023 | `US-MCP-BUILDER-R011.11` | `tests/test_mcp_builder_connector_scaffold.py::test_generated_package_passes_the_sdk_conformance_plugin` | SDK conformance plugin passes holds on a generated connector. |
