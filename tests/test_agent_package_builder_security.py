"""Security invariants for newly scaffolded agent packages."""

import ast
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
PYTHON_312_BASE = (
    "python:3.12-slim@sha256:"
    "57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de"
)


def _load_scaffold_module():
    spec = importlib.util.spec_from_file_location("_secure_scaffold_pkg", SCAFFOLD)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_local_templates_default_to_loopback():
    module = _load_scaffold_module()

    assert "ARG HOST=127.0.0.1" in module.DOCKERFILE
    assert "ARG HOST=0.0.0.0" not in module.DOCKERFILE
    assert "HOST=127.0.0.1" in module.ENV_EXAMPLE
    assert "/deployment/" in module.README_MD


def test_networked_compose_requires_auth_and_limits_host_publish():
    module = _load_scaffold_module()

    for compose in (module.AGENT_COMPOSE_YML, module.MCP_COMPOSE_YML):
        assert "AUTH_TYPE=${{AUTH_TYPE:?" in compose
        assert '"127.0.0.1:8000:8000"' in compose
        assert '"8000:8000"' not in compose


def test_generated_mcp_server_uses_governed_factory():
    module = _load_scaffold_module()

    assert "create_mcp_server(" in module.MCP_SERVER_PY
    assert "FastMCP(" not in module.MCP_SERVER_PY


def test_generated_api_client_has_outbound_request_boundaries():
    module = _load_scaffold_module()
    rendered = module.API_CLIENT_BASE.format()

    compile(rendered, "<generated-api-client>", "exec")
    assert "create_http_client(" in rendered
    assert "ResolvedTLSProfile" in rendered
    assert "tls_profile.httpx_kwargs()" in rendered
    assert "timeout=_REQUEST_TIMEOUT_S" in rendered
    assert "follow_redirects=False" in rendered
    assert "from ..error_authority import AGENT_ERROR_ACCEPT" in rendered
    assert 'headers = {"Accept": AGENT_ERROR_ACCEPT}' in rendered
    assert (
        "pin_egress=not tls_profile.proxy_url and not tls_profile.trust_env" in rendered
    )
    assert "_MAX_RESPONSE_BYTES" in rendered
    assert "self.session.stream(" in rendered


def test_generated_error_authority_has_agent_safe_negotiation():
    module = _load_scaffold_module()
    rendered = module.ERROR_AUTHORITY_PY

    compile(rendered, "<generated-error-authority>", "exec")
    assert "application/problem+json" in rendered
    assert "text/markdown" in rendered
    assert "text/html" in rendered
    assert "AGENT_ERROR_ACCEPT" in rendered
    assert "sanitize_for_persistence" in rendered
    assert "MAX_DETAIL_CHARS" in rendered
    assert "status in {401, 403}" in rendered
    assert '"Vary": "Accept"' in rendered
    assert "{pkg_dir}.error_authority" in module.INIT_PY


def test_generated_capability_discovery_is_bound_and_endpoint_free():
    module = _load_scaffold_module()

    assert "http_transport" in module.CAPABILITY_MCP_JSON
    assert "mcp_endpoint" not in module.AGENT_READINESS_JSON
    assert "a2a_endpoint" not in module.AGENT_READINESS_JSON


def test_generated_auth_uses_reference_only_runtime_without_pii_logs():
    module = _load_scaffold_module()
    rendered = module.AUTH_PY.format(short_name="example_provider")
    tree = ast.parse(rendered)
    imported_symbols = {
        (node.module, alias.name)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }

    compile(rendered, "<generated-auth>", "exec")
    assert "from agent_utilities.core import config as config_module" in rendered
    assert "config_module.AgentConfig" in rendered
    assert ("agent_utilities.core", "config") in imported_symbols
    assert ("agent_utilities.core.config", "AgentConfig") not in imported_symbols
    assert "resolve_provider_runtime_profile(" in module.AUTH_PY
    assert "provider_configs.{short_name}" in module.AUTH_PY
    assert "resolve_tls_verify" not in module.AUTH_PY
    assert "SSL_VERIFY" not in module.AUTH_PY
    assert "verify: bool" not in module.AUTH_PY
    assert "user_email" not in module.AUTH_PY


def test_generated_graphql_client_validates_url_and_sets_timeout():
    module = _load_scaffold_module()

    assert "urlsplit(rendered_url)" in module.GQL_PY
    assert "timeout=30" in module.GQL_PY
    assert "len(query_str) > 1_000_000" in module.GQL_PY


def test_generated_deployment_docs_are_current_only_and_tls_bound():
    module = _load_scaffold_module()
    docs = module.README_MD + module.DOCS_DEPLOYMENT_MD

    assert 'MCP_TOOL_MODE": "intent' in docs
    assert "agent-os-genesis" not in docs
    assert "your_token" not in docs
    assert ".arpa" not in docs
    assert "behind Caddy" not in docs
    assert "https://service.example.invalid/mcp" in docs
    assert "authenticated TLS ingress" in docs
    assert "MCP_ALLOWED_HOSTS" in docs
    assert "--cap-drop=ALL" in docs
    assert "@sha256:<digest>" in docs


def test_generated_packaging_is_current_full_and_nonrecursive(tmp_path):
    module = _load_scaffold_module()
    module.scaffold("example-provider", output_dir=str(tmp_path))
    root = tmp_path / "example-provider"
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    agents_md = (root / "AGENTS.md").read_text(encoding="utf-8")
    installation_md = (root / "docs" / "installation.md").read_text(encoding="utf-8")
    dockerfile = (root / "docker" / "Dockerfile").read_text(encoding="utf-8")
    debug_dockerfile = (root / "docker" / "debug.Dockerfile").read_text(
        encoding="utf-8"
    )
    parity_manifest = PARITY_MANIFEST.read_text(encoding="utf-8")
    generated_text = "\n".join(
        path.read_text(encoding="utf-8") for path in root.rglob("*") if path.is_file()
    )

    assert 'requires-python = ">=3.12, <3.15"' in pyproject
    assert 'target-version = "py312"' in pyproject
    assert 'python_version = "3.12"' in pyproject
    assert "py310" not in pyproject
    assert 'python_version = "3.10"' not in pyproject
    assert "Language/Version: Python 3.12–3.14" in agents_md
    assert "Python 3.12–3.14" in installation_md
    assert "Python 3.11" not in agents_md
    assert "Python 3.11" not in installation_md
    assert dockerfile.count(PYTHON_312_BASE) == 2
    assert debug_dockerfile.count(PYTHON_312_BASE) == 1
    assert "Python 3.11" not in generated_text
    assert "python:3.11" not in generated_text
    assert '"agent-utilities[mcp]>=1.27.1,<2.0.0"' in pyproject
    assert '"epistemic-graph[full]>=2.23.1,<3.0.0"' in pyproject
    assert '"agent-utilities[agent-runtime,logfire]>=1.27.1,<2.0.0"' in pyproject
    assert "`agent-utilities[mcp]>=1.27.1,<2.0.0`" in parity_manifest
    assert "`epistemic-graph[full]>=2.23.1,<3.0.0`" in parity_manifest
    assert "agent-utilities[mcp]>=2.0.0" not in parity_manifest
    assert "epistemic-graph[full]>=3.0.0" not in parity_manifest
    assert PYTHON_312_BASE.removeprefix("python:3.12-slim@") in parity_manifest
    assert "example-provider[" not in pyproject
    assert not (root / ".env").exists()
    assert "SSL_VERIFY" not in (root / "mcp_config.json").read_text(encoding="utf-8")
    assert not (root / "example_provider" / "api_client.py").exists()
    assert (root / "example_provider" / "error_authority.py").is_file()
    assert (root / "tests" / "test_error_authority.py").is_file()
    assert (root / "scripts" / "agent_readiness_tck.py").is_file()
    assert (root / ".well-known" / "api-catalog").is_file()
    assert (root / ".well-known" / "mcp-server-card.json").is_file()
    assert (root / ".well-known" / "agent-skills.json").is_file()
    catalog = (root / ".well-known" / "api-catalog").read_text(encoding="utf-8")
    assert "https://service.example.invalid" not in catalog
    assert "https://www.rfc-editor.org/info/rfc9727" in catalog
