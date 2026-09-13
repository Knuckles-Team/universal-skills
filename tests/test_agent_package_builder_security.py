"""Security and dependency invariants for the SDK-retargeted connector scaffold
(RF-ADR-009, lane BUILDER-RETARGET). See PARITY_MANIFEST.md for the generated-
file contract this exercises.
"""

from __future__ import annotations

import importlib.util
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
