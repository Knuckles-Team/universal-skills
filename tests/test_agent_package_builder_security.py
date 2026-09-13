"""Security and dependency invariants for the SDK-retargeted connector scaffold
(RF-ADR-009, lane BUILDER-RETARGET). See PARITY_MANIFEST.md for the generated-
file contract this exercises.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

SCAFFOLD = (
    Path(__file__).parents[1]
    / "universal_skills"
    / "agent-tools"
    / "agent-package-builder"
    / "scripts"
    / "scaffold_package.py"
)
PARITY_MANIFEST = SCAFFOLD.parent.parent / "PARITY_MANIFEST.md"


def _load_scaffold_module():
    spec = importlib.util.spec_from_file_location("_secure_scaffold_pkg", SCAFFOLD)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scaffolded_package_depends_only_on_the_sdk_and_eg_client(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")

    assert "agent-connector-sdk>=" in pyproject
    assert "epistemic-graph>=" in pyproject
    # "agent-utilities" appears only in the prose comment naming the forbidden
    # dependency (RF-ADR-009 phase order) — never as a version specifier or an
    # import.
    assert '"agent-utilities' not in pyproject
    generated_py = "\n".join(
        path.read_text(encoding="utf-8")
        for path in root.rglob("*.py")
        if path.is_file()
    )
    assert "import agent_utilities" not in generated_py
    assert "from agent_utilities" not in generated_py


def test_generated_mcp_server_uses_the_sdk_factory_and_tool_surface():
    module = _load_scaffold_module()

    assert "create_mcp_server(" in module.MCP_SERVER_PY
    assert "register_tool_surface(" in module.MCP_SERVER_PY
    assert "ConnectorContent(" in module.MCP_SERVER_PY
    assert "FastMCP(" not in module.MCP_SERVER_PY
    assert "agent_connector_sdk" in module.MCP_SERVER_PY


def test_mcp_server_only_passes_host_and_port_for_networked_transports():
    module = _load_scaffold_module()

    assert 'if args.transport == "stdio":' in module.MCP_SERVER_PY
    assert "mcp.run(transport=args.transport)" in module.MCP_SERVER_PY


def test_credentials_are_references_never_raw_values(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"

    env_example = (root / ".env.example").read_text(encoding="utf-8")
    assert "env://" in env_example or "openbao://" in env_example
    assert not (root / ".env").exists()

    credentials_py = (root / "example_provider" / "credentials.py").read_text(
        encoding="utf-8"
    )
    assert "agent_connector_sdk.credentials" in credentials_py
    assert "parse_secret_reference" in credentials_py
    assert "SSL_VERIFY" not in credentials_py
    assert "verify=False" not in credentials_py


def test_generated_manifest_has_a_valid_sync_preset(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"
    manifest = (root / "connector_manifest.yml").read_text(encoding="utf-8")

    assert "connector: example-provider" in manifest
    assert "sync:" in manifest
    assert "tool_schema_sha256:" in manifest
    assert "provenance:" in manifest
    assert (root / "connectors" / "mcp_source_presets.json").is_file()
    assert (root / "connectors" / "tool_schema_fingerprints.json").is_file()
    assert (root / "scripts" / "pin_tool_schema.py").is_file()


def test_content_is_served_as_native_mcp_primitives(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"

    assert (root / "skills" / "example-provider-reader" / "SKILL.md").is_file()
    assert (root / "prompts" / "example-provider.json").is_file()
    assert (root / "ontology" / "example-provider.ttl").is_file()
    assert (root / "ontology" / "shapes" / "example-provider.shapes.ttl").is_file()
    prompt = (root / "prompts" / "example-provider.json").read_text(encoding="utf-8")
    assert '"core_directive"' in prompt


def test_docs_publish_from_pages_not_docs(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"

    assert not (root / "docs").exists()
    assert (root / "pages" / "index.md").is_file()
    mkdocs = (root / "mkdocs.yml").read_text(encoding="utf-8")
    assert "docs_dir: pages" in mkdocs
    assert "theme:" not in mkdocs
    assert "markdown_extensions:" not in mkdocs


def test_pages_workflow_calls_the_shared_reusable_workflow_pinned_to_a_sha(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"
    pages_workflow = (root / ".github" / "workflows" / "pages.yml").read_text(
        encoding="utf-8"
    )

    assert (
        "uses: Knuckles-Team/pipelines/.github/workflows/pages_pipeline.yml@"
        in pages_workflow
    )
    sha = re.search(r"pages_pipeline\.yml@([0-9a-f]{40})", pages_workflow)
    assert sha is not None, "pages.yml must pin the reusable workflow to a full SHA"
    assert "content_source: pages" in pages_workflow
    assert "shared_theme_enabled: true" in pages_workflow
    assert "agent_readiness_enabled: true" in pages_workflow
    assert "mkdocs build" not in pages_workflow


def test_agent_readiness_input_matches_both_canonical_schemas(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"

    readiness = json.loads(
        (root / "pages" / "agent-readiness.json").read_text(encoding="utf-8")
    )
    schema = json.loads(
        (root / "pages" / "agent-readiness.schema.json").read_text(encoding="utf-8")
    )
    canonical_schema = json.loads(
        (SCAFFOLD.parent / "agent_readiness_schema.json").read_text(encoding="utf-8")
    )
    assert schema == canonical_schema

    assert readiness["schema_version"] == "agent-readiness/v1"
    assert readiness["applicability"]["discoverability"] is True
    for name in ("api", "mcp", "a2a", "skills"):
        assert readiness["capabilities"][name] == {"applicable": False}
    assert (root / "scripts" / "generate_agent_readiness.py").is_file()
    generator_script = (root / "scripts" / "generate_agent_readiness.py").read_text(
        encoding="utf-8"
    )
    assert "sys.modules[spec.name] = module" in generator_script


def test_precommit_references_shared_hooks_with_a_placeholder_revision():
    module = _load_scaffold_module()
    precommit = module.PRECOMMIT_CONFIG

    assert "@@github_org@@/pipelines" in precommit
    assert "REPLACE_WITH_SHARED_HOOKS_REV" in precommit
    assert "SHARED-HOOKS" in precommit
    for hook_id in (
        "complexity-staged",
        "kiss-staged",
        "clone-dupehound-changed-functions",
        "check-secret-history",
        "security-sanitizer",
        "guardrail-tracked-privacy",
        "check-root-hygiene",
        "dependency-audit",
        "check-orphan-modules",
    ):
        assert hook_id in precommit
    # The lane brief: reference the shared hooks by id, never copy their
    # scripts into the generated package.
    assert "check_scanners.py" not in precommit
    assert "run_kiss.sh" not in precommit


def test_no_scanner_gate_scripts_are_copied_into_the_package(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"

    assert not (root / "scripts" / "check_scanners.py").exists()
    assert not (root / "scripts" / "run_kiss.sh").exists()
    assert not (root / ".cccc.toml").exists()
    assert not (root / ".kiss").exists()
    assert not (root / ".github" / "workflows" / "scanners.yml").exists()


def test_local_defaults_are_loopback_and_networked_publish_requires_auth():
    module = _load_scaffold_module()

    assert "ARG HOST=127.0.0.1" in module.DOCKERFILE
    assert "HOST=127.0.0.1" in module.ENV_EXAMPLE
    assert "AUTH_TYPE=${AUTH_TYPE:?" in module.MCP_COMPOSE_YML
    assert '"127.0.0.1:8000:8000"' in module.MCP_COMPOSE_YML
    assert '"8000:8000"' not in module.MCP_COMPOSE_YML


def test_no_generated_dotenv_or_raw_secret_in_mcp_config(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"

    assert not (root / ".env").exists()
    mcp_config = (root / "mcp_config.json").read_text(encoding="utf-8")
    assert "SSL_VERIFY" not in mcp_config
    assert "openbao://" not in mcp_config  # config carries no resolved reference


def test_scaffold_rerun_is_idempotent_and_preserves_project_owned_edits(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"
    manifest_path = root / "connector_manifest.yml"
    manifest_path.write_text(
        manifest_path.read_text(encoding="utf-8") + "\n# operator-owned\n",
        encoding="utf-8",
    )
    expected = manifest_path.read_bytes()

    module.scaffold("example-provider", output_dir=str(tmp_path))

    assert manifest_path.read_bytes() == expected


def test_readme_and_agents_md_describe_the_sdk_dependency(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"

    readme = (root / "README.md").read_text(encoding="utf-8")
    agents_md = (root / "AGENTS.md").read_text(encoding="utf-8")
    assert "agent-connector-sdk" in readme
    assert "agent-connector-sdk" in agents_md
    assert "agent-utilities" not in readme
    # AGENTS.md deliberately names agent-utilities once, in the negative
    # constraint forbidding it as a dependency (RF-ADR-009 phase order).
    assert agents_md.count("agent-utilities") == 1
    assert "never" in agents_md.lower()


# ── Lane BUILDER-API-CLIENT: the generated connector has a real API client ──


def test_generated_api_client_is_built_only_from_the_sdk_http_layer(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"
    api_client = (root / "example_provider" / "api_client.py").read_text(
        encoding="utf-8"
    )

    assert "agent_connector_sdk.http.client" in api_client
    assert "agent_connector_sdk.tls.resolve" in api_client
    assert "agent_connector_sdk.auth.static" in api_client
    assert "def build_client(" in api_client
    assert "def build_client_for(" in api_client
    assert "resolve_tls_profile(" in api_client
    # No raw HTTP client library, and no agent-utilities transport layer.
    assert "import requests" not in api_client
    assert "httpx.get(" not in api_client
    assert "httpx.post(" not in api_client
    assert "agent_utilities" not in api_client


def test_generated_tool_calls_the_api_client_not_demo_data(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"
    domain_tool = (root / "example_provider" / "mcp" / "mcp_reader.py").read_text(
        encoding="utf-8"
    )

    assert "from example_provider.api_client import build_client" in domain_tool
    assert "build_client()" in domain_tool
    assert "arequest_json(" in domain_tool
    assert "ToolPage" in domain_tool
    # The old in-memory demo generator is gone.
    assert "_ITEMS" not in domain_tool
    assert "action: str" not in domain_tool
    assert "params_json" not in domain_tool


def test_generated_sync_preset_matches_the_tool_not_action_params_json(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"
    manifest = json.loads(
        (root / "connectors" / "mcp_source_presets.json").read_text(encoding="utf-8")
    )
    preset = manifest["reader"]

    assert preset["params_style"] == "args"
    assert preset["action"] == ""
    assert preset["pagination"] == "cursor"
    assert preset["cursor_param"] == "cursor"
    assert preset["cursor_path"] == "next_cursor"
    assert preset["more_path"] == "has_more"


def test_auth_mode_selects_the_matching_sdk_helper(tmp_path):
    module = _load_scaffold_module()
    expectations = {
        "bearer": "bearer_auth(",
        "basic": "basic_auth(",
        "api_key": "api_key_auth(",
        "client_credentials": "client_credentials_auth(",
        "delegated": "DelegatedTokenAuth(",
    }
    for auth_mode, expected_call in expectations.items():
        name = f"example-{auth_mode}".replace("_", "-")
        module.scaffold(name, output_dir=str(tmp_path), auth_mode=auth_mode)
        pkg_dir = name.replace("-", "_")
        api_client = (tmp_path / name / pkg_dir / "api_client.py").read_text(
            encoding="utf-8"
        )
        assert expected_call in api_client


def test_pagination_mode_shapes_the_tool_signature_and_preset(tmp_path):
    module = _load_scaffold_module()
    expectations = {
        "cursor": "cursor: str | None = None",
        "page": "page: int = 0",
        "offset": "offset: int = 0",
    }
    for pagination, expected_param in expectations.items():
        name = f"example-{pagination}"
        module.scaffold(name, output_dir=str(tmp_path), pagination=pagination)
        pkg_dir = name.replace("-", "_")
        domain_tool = (tmp_path / name / pkg_dir / "mcp" / "mcp_reader.py").read_text(
            encoding="utf-8"
        )
        assert expected_param in domain_tool
        preset = json.loads(
            (tmp_path / name / "connectors" / "mcp_source_presets.json").read_text(
                encoding="utf-8"
            )
        )["reader"]
        assert preset["pagination"] == pagination


def test_generated_tests_prove_the_api_client_end_to_end(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"
    test_api_client = (root / "tests" / "test_api_client.py").read_text(
        encoding="utf-8"
    )

    assert "ScriptedHttpServer" in test_api_client
    assert "run_http_client_suite" in test_api_client
    assert "HttpProblemError" in test_api_client
    assert "call_tool(" in test_api_client


def test_oauth_auth_modes_skip_the_generic_conformance_kit_honestly(tmp_path):
    module = _load_scaffold_module()
    for auth_mode in ("client_credentials", "delegated"):
        name = f"example-{auth_mode}".replace("_", "-")
        module.scaffold(name, output_dir=str(tmp_path), auth_mode=auth_mode)
        test_api_client = (tmp_path / name / "tests" / "test_api_client.py").read_text(
            encoding="utf-8"
        )
        # run_http_client_suite assumes a factory that is self-contained given
        # only a base URL; an OAuth 2.0 client mints its token from a
        # separately configured endpoint, so it is not imported/called here,
        # honestly documented (in prose) rather than silently omitted.
        assert "from agent_connector_sdk.testing.http_clients" not in test_api_client
        assert "run_http_client_suite(" not in test_api_client
        assert "is not run here" in test_api_client
        assert "ScriptedHttpServer" in test_api_client
        assert "HttpProblemError" in test_api_client


def test_openapi_hint_seeds_base_url_and_list_path(tmp_path):
    module = _load_scaffold_module()
    openapi_path = tmp_path / "openapi.json"
    openapi_path.write_text(
        json.dumps(
            {
                "openapi": "3.0.3",
                "servers": [{"url": "https://vendor.example.invalid/v1"}],
                "paths": {"/widgets": {"get": {"operationId": "listWidgets"}}},
            }
        ),
        encoding="utf-8",
    )
    module.scaffold(
        "example-provider", output_dir=str(tmp_path), openapi=str(openapi_path)
    )
    root = tmp_path / "example-provider"

    env_example = (root / ".env.example").read_text(encoding="utf-8")
    domain_tool = (root / "example_provider" / "mcp" / "mcp_reader.py").read_text(
        encoding="utf-8"
    )
    assert "https://vendor.example.invalid/v1" in env_example
    assert '_LIST_PATH = "/widgets"' in domain_tool
