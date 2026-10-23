"""Security invariants for newly scaffolded agent packages."""

import ast
import importlib.util
import tomllib
from pathlib import Path

import pytest

SCAFFOLD = (
    Path(__file__).parents[1]
    / "universal_skills"
    / "agent-tools"
    / "mcp-builder"
    / "scripts"
    / "scaffold_package.py"
)
PYTHON_312_BASE = (
    "python:3.14-slim@sha256:"
    "a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170"
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
    assert "--host 127.0.0.1" in module.README_MD
    assert '"HOST": "127.0.0.1"' in module.README_MD


def test_networked_compose_requires_auth_and_limits_host_publish():
    module = _load_scaffold_module()

    for compose in (module.MCP_COMPOSE_YML,):
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
    assert "HttpClientOptions(" in rendered
    assert "tls=tls_profile" in rendered
    assert "timeout=_REQUEST_TIMEOUT_S" in rendered
    assert 'kwargs["follow_redirects"] = False' in rendered
    assert 'if "timeout" in kwargs:' in rendered
    assert "Redirect following is disabled" in rendered
    assert "from ..error_authority import AGENT_ERROR_ACCEPT" in rendered
    assert 'headers={"Accept": AGENT_ERROR_ACCEPT}' in rendered
    imports = {
        node.module
        for node in ast.walk(ast.parse(rendered))
        if isinstance(node, ast.ImportFrom)
    }
    assert "agent_connector_sdk.http.client" in imports
    assert "agent_connector_sdk.http.options" in imports
    assert not any(name and name.startswith("agent_utilities") for name in imports)
    assert "_MAX_RESPONSE_BYTES" in rendered
    assert "self.session.stream(" in rendered


def test_generated_error_authority_has_agent_safe_negotiation():
    module = _load_scaffold_module()
    rendered = module.ERROR_AUTHORITY_PY
    representations = module.ERROR_RENDERING_PY

    compile(rendered, "<generated-error-authority>", "exec")
    assert "application/problem+json" in representations
    assert "text/markdown" in representations
    assert "text/html" in representations
    assert "AGENT_ERROR_ACCEPT" in rendered
    assert "sanitize_for_persistence" in rendered
    assert "MAX_DETAIL_CHARS" in rendered
    assert "status in {401, 403}" in rendered
    assert '"Vary": "Accept"' in representations
    assert "{pkg_dir}.error_authority" in module.INIT_PY


def test_generated_capability_discovery_is_bound_and_endpoint_free():
    module = _load_scaffold_module()

    assert "http_transport" in module.CAPABILITY_MCP_JSON
    assert "mcp_endpoint" not in module.AGENT_READINESS_JSON
    assert "a2a_endpoint" not in module.AGENT_READINESS_JSON


def test_generated_auth_uses_reference_only_runtime_without_pii_logs():
    module = _load_scaffold_module()
    rendered = module.AUTH_PY.format(
        short_name="example_provider", upper_name="EXAMPLE_PROVIDER"
    )
    tree = ast.parse(rendered)
    imported_symbols = {
        (node.module, alias.name)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }

    compile(rendered, "<generated-auth>", "exec")
    assert ("agent_connector_sdk.auth.static", "bearer_auth") in imported_symbols
    assert (
        "agent_connector_sdk.auth.delegation",
        "DelegatedTokenAuth",
    ) in imported_symbols
    assert (
        "agent_connector_sdk.tls.resolve",
        "resolve_tls_profile",
    ) in imported_symbols
    assert not any(
        name and name.startswith("agent_utilities") for name, _ in imported_symbols
    )
    assert 'bearer_auth(setting("EXAMPLE_PROVIDER_TOKEN_REF", ""))' in rendered
    assert 'resolve_tls_profile("example_provider")' in rendered
    assert 'resolve_tls_profile("oidc")' in rendered
    assert "resources.callback(tls.cleanup)" in rendered
    assert "resources.callback(token_tls.cleanup)" in rendered
    assert "resources.callback(token_client.close)" in rendered
    assert "resources.callback(client.close)" in rendered
    assert "resolve_tls_verify" not in rendered
    assert "SSL_VERIFY" not in rendered
    assert "verify: bool" not in rendered
    assert "user_email" not in rendered


def test_generated_graphql_uses_bounded_sdk_client_and_rejects_invalid_results(
    tmp_path, monkeypatch
):
    module = _load_scaffold_module()
    tree = ast.parse(module.GQL_PY.format())
    client_import = [
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "api.api_client_base"
    ]
    assert len(client_import) == 1 and client_import[0].level == 1
    assert [alias.name for alias in client_import[0].names] == ["ApiClientBase"]
    # Only the outbound client is replaced: import the actual rendered class
    # so bad input and partial provider failures cannot become successes.
    package = tmp_path / "sdk_graphql_fixture"
    (package / "api").mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "api" / "__init__.py").write_text("")
    (package / "api" / "api_client_base.py").write_text("class ApiClientBase: pass\n")
    (package / "graphql.py").write_text(module.GQL_PY.format())
    monkeypatch.syspath_prepend(str(tmp_path))
    graphql = importlib.import_module("sdk_graphql_fixture.graphql")
    client = graphql.GraphQL()
    calls = []
    client.request = lambda *args, **kwargs: (
        calls.append((args, kwargs)) or {"data": {"ok": True}}
    )
    for query in ("", " ", "x" * 1_000_001, None):
        with pytest.raises(ValueError, match="input boundary"):
            client.execute_gql(query)
    assert calls == []
    assert client.execute_gql("query { status }") == {"data": {"ok": True}}
    assert calls[0][0][0] == "POST"
    assert calls[0][1]["json"]["query"] == "query { status }"
    client.request = lambda *args, **kwargs: {
        "data": {"ok": True},
        "errors": [{"message": "partial"}],
    }
    with pytest.raises(RuntimeError, match="partial results"):
        client.execute_gql("query { status }")


def test_generated_deployment_docs_are_current_only_and_tls_bound():
    module = _load_scaffold_module()
    docs = module.README_MD + module.DOCS_DEPLOYMENT_MD

    assert "MCP_TOOL_MODE" not in docs
    assert "agent-os-genesis" not in docs
    assert "your_token" not in docs
    assert ".arpa" not in docs
    assert "behind Caddy" not in docs
    assert "https://service.example.invalid/mcp" in docs
    assert "authenticated TLS ingress" in docs
    assert "MCP_ALLOWED_HOSTS" in docs
    assert "--cap-drop=ALL" in docs
    assert "@sha256:<digest>" in docs


@pytest.mark.parametrize("has_agent", [False])
def test_generated_packaging_uses_sdk_and_optional_runtime_without_recursive_extras(
    tmp_path,
    has_agent,
):
    module = _load_scaffold_module()
    module.scaffold(
        "example-provider",
        output_dir=str(tmp_path),
        pkg_types="api_client,mcp" + (",agent" if has_agent else ""),
    )
    root = tmp_path / "example-provider"
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    agents_md = (root / "AGENTS.md").read_text(encoding="utf-8")
    installation_md = (root / "docs" / "installation.md").read_text(encoding="utf-8")
    dockerfile = (root / "docker" / "Dockerfile").read_text(encoding="utf-8")
    debug_dockerfile = (root / "docker" / "debug.Dockerfile").read_text(
        encoding="utf-8"
    )
    generated_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in root.rglob("*")
        if path.is_file() and path.suffix != ".png"
    )

    assert 'requires-python = ">=3.12"' in pyproject
    assert 'target-version = "py312"' in pyproject
    assert 'python_version = "3.12"' in pyproject
    assert "py310" not in pyproject
    assert 'python_version = "3.10"' not in pyproject
    assert "Python 3.12–3.14" in installation_md
    assert "Python 3.11" not in agents_md
    assert "Python 3.11" not in installation_md
    assert dockerfile.count(PYTHON_312_BASE) == 1
    assert debug_dockerfile.count(PYTHON_312_BASE) == 1
    assert "Python 3.11" not in generated_text
    assert "python:3.11" not in generated_text
    metadata = tomllib.loads(pyproject)
    dependencies = metadata["project"]["dependencies"]
    extras = metadata["project"]["optional-dependencies"]
    assert "agent-connector-sdk[mcp]>=0.3.12,<1.0.0" in dependencies
    assert not any(
        requirement.startswith(("agent-utilities", "epistemic-graph"))
        for requirement in dependencies
    )
    if has_agent:
        assert any(
            requirement.startswith("agent-utilities[agent-runtime")
            for requirement in extras["agent"]
        )
    else:
        assert "agent" not in extras
        assert not any(
            requirement.startswith("agent-utilities") for requirement in extras["all"]
        )
    assert all(
        "epistemic-graph[full]" not in requirement
        for group in extras.values()
        for requirement in group
    )
    assert (root / "example_provider" / "agent_server.py").exists() is has_agent
    assert (root / "example_provider" / "mcp_server.py").is_file()
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
