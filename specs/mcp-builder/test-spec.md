# US-MCP-BUILDER — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `US-MCP-BUILDER-R011.1` | `tests/test_mcp_builder_connector_scaffold.py::test_scaffold_emits_exactly_the_minimal_tree` | Exact 29-file connector-owned tree holds on a generated connector. |
| T-002 | `US-MCP-BUILDER-R011.2` | `tests/test_mcp_builder_connector_scaffold.py::test_generation_is_deterministic` | Deterministic output holds on a generated connector. |
| T-003 | `US-MCP-BUILDER-R011.3` | `tests/test_mcp_builder_connector_scaffold.py::test_identity_and_version_live_in_pyproject_only` | Identity and version in pyproject only holds on a generated connector. |
| T-004 | `US-MCP-BUILDER-R011.4` | `tests/test_mcp_builder_connector_scaffold.py::test_workflows_call_the_shared_pipelines_for_pypi_and_docker` | Shared workflows for release and PR holds on a generated connector. |
| T-005 | `US-MCP-BUILDER-R011.5` | `tests/test_mcp_builder_connector_scaffold.py::test_one_tool_per_operation_with_risk_annotations` | One tool per operation with risk classes holds on a generated connector. |
| T-006 | `US-MCP-BUILDER-R011.6` | `tests/test_mcp_builder_connector_scaffold.py::test_sources_load_as_typed_declaration_with_no_manifest_file` | Sources declared as data holds on a generated connector. |
| T-007 | `US-MCP-BUILDER-R011.7` | `tests/test_mcp_builder_connector_scaffold.py::test_prompt_skill_and_ontology_are_served_over_mcp` | Content served over MCP holds on a generated connector. |
| T-008 | `US-MCP-BUILDER-R011.8` | `tests/test_mcp_builder_connector_scaffold.py::test_ontology_rolls_up_to_a_core_class_and_never_imports_the_parent` | Ontology rolls up to a core class holds on a generated connector. |
| T-009 | `US-MCP-BUILDER-R011.9` | `tests/test_mcp_builder_connector_scaffold.py::test_pipelines_connector_gates_pass` | Pipelines connector gates pass holds on a generated connector. |
| T-010 | `US-MCP-BUILDER-R011.10` | `tests/test_mcp_builder_connector_scaffold.py::test_ontology_graph_check_passes_against_the_core_ontology` | Ontology graph check passes holds on a generated connector. |
| T-011 | `US-MCP-BUILDER-R011.11` | `tests/test_mcp_builder_connector_scaffold.py::test_generated_package_passes_the_sdk_conformance_plugin` | SDK conformance plugin passes holds on a generated connector. |
| T-012 | `US-MCP-BUILDER-R011.12` | `tests/test_mcp_builder_connector_scaffold.py::test_client_is_one_sdk_auth_declaration_with_no_own_transport` | Client from one SDK auth declaration holds on a generated connector. |
| T-013 | `US-MCP-BUILDER-R011.13` | `tests/test_mcp_builder_connector_scaffold.py::test_optional_dependencies_are_sdk_extras_only` | Dependencies through SDK extras holds on a generated connector. |
| T-014 | `US-MCP-BUILDER-R011.1` | `tests/test_mcp_builder_connector_scaffold.py::test_generated_pages_caller_has_a_safe_shared_theme_preflight` | A generated Pages caller leaves shared theme disabled until canonical provider assets are generated; no theme assets are duplicated in the minimal tree. |
| T-015 | `US-MCP-BUILDER-R011.14` | `tests/test_mcp_builder_connector_scaffold.py::test_connector_inherits_the_organization_constitution` | The generated constitution links the organization file, names its version and holds the connector articles. |
| T-016 | `US-MCP-BUILDER-R012.1` | `tests/test_mcp_builder_connector_scaffold.py::test_wrap_project_is_deterministic` | Deterministic whole project. |
| T-017 | `US-MCP-BUILDER-R012.2` | `tests/test_mcp_builder_connector_scaffold.py::test_wrap_mounts_the_upstream_with_governance_and_no_rest_client` | Namespaced upstream with governance. |
| T-018 | `US-MCP-BUILDER-R012.3` | `tests/test_mcp_builder_connector_scaffold.py::test_wrapped_repo_passes_its_own_gates` | The generated repository passes its own gates. |
| T-019 | `US-MCP-BUILDER-R013.1` | `tests/test_mcp_builder_connector_scaffold.py::test_deploy_bundle_is_emitted_beside_the_repo` | Bundle layout. |
| T-020 | `US-MCP-BUILDER-R013.2` | `tests/test_mcp_builder_connector_scaffold.py::test_deploy_bundle_holds_no_secret_value_and_installs_the_release` | No secret value and release-only image. |
| T-021 | `US-MCP-BUILDER-R013.3` | `tests/test_mcp_builder_connector_scaffold.py::test_deploy_profile_supplies_site_values` | Site values from a deploy profile. |
