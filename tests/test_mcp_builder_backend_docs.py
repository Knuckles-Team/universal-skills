"""Backend documentation must match generated source and execution contracts."""

from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest
import yaml


SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)
CONTEXT = {
    "package_name": "docs-example",
    "pkg_dir": "docs_example",
    "short_name": "docs-example",
    "display_name": "Docs Example",
    "concept_prefix": "DOCS",
    "upper_name": "DOCS_EXAMPLE",
    "description": "Example connector",
    "badge_lines": "",
    "mcp_cmd": "docs-example-mcp",
    "agent_cmd": "docs-example-agent",
    "date": "2026-10-12",
    "agent_port": "9000",
    "gql_optional_module": "",
    "gql_all_extend": "",
}


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _templates():
    tree = ast.parse((SCRIPTS / "scaffold_package.py").read_text())
    return {
        node.targets[0].id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    }


def test_api_backend_preserves_shared_templates():
    selector = _load("backend_surfaces").select_backend_template
    for name, template in _templates().items():
        assert selector(name, template, "api_client") == template
    assert selector("UNKNOWN", "unchanged", "cli") == "unchanged"
    with pytest.raises(ValueError, match="unsupported connector backend"):
        selector("README_MD", "text", "unknown")


def test_cli_docs_compose_without_agent_surfaces():
    backend = _load("backend_surfaces")
    surface = _load("surface_templates")
    names = {
        *backend._REPLACEMENTS,
        "ENV_EXAMPLE",
        "DOCS_USAGE_MD",
        "DOCS_PLATFORM_MD",
    }
    templates = _templates()
    rendered = {
        name: backend.select_backend_template(
            name, surface.select_template(name, templates[name], False), "cli"
        ).format(**CONTEXT)
        for name in names
    }
    combined = "\n".join(rendered.values())
    for setting in ("_BASE_URL", "_TOKEN_REF", "_TLS_PROFILE", "_ALLOW_PLAINTEXT"):
        assert setting not in combined
    assert "params_json" not in combined
    assert "docs_example.auth" not in combined
    assert "`api/`" not in combined
    assert "`docs_example/api/`" not in combined
    assert "DOCS_EXAMPLE_EXECUTABLE" in rendered["ENV_EXAMPLE"]
    assert "10-second" in rendered["DOCS_USAGE_MD"]
    assert "64 KiB" in rendered["DOCS_USAGE_MD"]
    assert "POSIX" in rendered["DOCS_INSTALLATION_MD"]
    assert "--version" in rendered["DOCS_USAGE_MD"]
    assert "from docs_example.cli import get_client" in rendered["DOCS_USAGE_MD"]
    assert "authenticated TLS ingress" in rendered["DOCS_DEPLOYMENT_MD"]
    assert "docs-example-agent" not in rendered["README_MD"]
    assert "Run the A2A agent server" not in rendered["DOCS_DEPLOYMENT_MD"]


@pytest.mark.parametrize("backend", ["api_client", "cli"])
def test_spec_contracts_select_backend_without_inventing_receipts(backend):
    renderer = _load("spec_templates").render_spec_files
    files = renderer(dict(CONTEXT, backend=backend))
    status = json.loads(files["specs/docs-example/status.json"])
    assert len(status["requirements"]) == 5
    assert status["delivery_state"] == "SPECIFIED"
    assert all(
        row["delivery_state"] == "SPECIFIED"
        and row["landed_in"] == []
        and row["verified_by"] == []
        for row in status["requirements"]
    )
    text = "\n".join(files.values())
    if backend == "cli":
        assert "Executable configuration" in text
        assert "Bounded process execution" in text
        assert "docs_example/cli.py" in text and "tests/test_cli.py" in text
        assert "Bounded CLI adapter" in files["docs/architecture.md"]
        for obsolete in (
            "auth.py",
            "api_client_base.py",
            "test_auth.py",
            "HTTP client",
            "Credential references",
        ):
            assert obsolete not in text
    else:
        assert files == renderer(CONTEXT)
        assert "docs_example/auth.py" in text and "tests/test_api_wrapper.py" in text
        assert "Connector API client" in files["docs/architecture.md"]


@pytest.mark.parametrize("backend", ["api_client", "cli"])
def test_generated_backend_documents_resolve_real_source_paths(backend, tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "scaffold_package.py"),
            "docs-example",
            "--type",
            f"{backend},mcp",
            "--output-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    root = tmp_path / "docs-example"
    spec = root / "specs/docs-example"
    code_paths = []
    documents = [*spec.glob("*.md"), root / "docs/architecture.md"]
    for document in documents:
        text = document.read_text()
        for declaration in re.findall(r"^Code:\s*(.+)$", text, re.MULTILINE):
            for source in declaration.split():
                target = (document.parent / source).resolve()
                assert target.is_file(), (document, source)
                code_paths.append(target)
        for test_path in re.findall(r"`(tests/[\w/.-]+\.py)(?:::[\w]+)?`", text):
            assert (root / test_path).is_file(), test_path
    expected = "docs_example/cli.py" if backend == "cli" else "docs_example/auth.py"
    assert root / expected in code_paths
    assert not (root / "docs_example/agent_server.py").exists()
    init = (root / "docs_example/__init__.py").read_text()
    assert "docs_example.agent_server" not in init
    assert "_AGENT_AVAILABLE" not in init
    configuration = json.loads((root / "mcp_config.json").read_text())
    settings = configuration["mcpServers"]["docs-example"]["env"]
    expected_key = (
        "DOCS_EXAMPLE_EXECUTABLE"
        if backend == "cli"
        else "DOCS_EXAMPLE_ALLOW_PLAINTEXT"
    )
    assert settings[expected_key] == ("" if backend == "cli" else "false")
    compose = yaml.safe_load((root / "docker/mcp.compose.yml").read_text())
    for service in compose["services"].values():
        declarations = service["environment"]
        assert any(value.startswith(expected_key + "=") for value in declarations)
        if backend == "cli":
            assert not any("ALLOW_PLAINTEXT" in value for value in declarations)
            assert any(
                "set-absolute-executable-path-inside-container" in value
                for value in declarations
            )
    docs = "\n".join(path.read_text() for path in (root / "docs").glob("*.md"))
    if backend == "cli":
        assert "DOCS_EXAMPLE_EXECUTABLE" in docs
        assert "_BASE_URL" not in docs and "_TOKEN_REF" not in docs
        assert not (root / "docs_example/auth.py").exists()
        assert not (root / "docs_example/api").exists()
        assert not list((root / "docs_example").glob("*_models.py"))
        assert not (root / "tests/test_auth.py").exists()
        assert not (root / "tests/test_api_wrapper.py").exists()
        assert (root / "tests/conftest.py").read_text() == ""
        assert not (root / "scripts/verify_api_integration.py").exists()
        assert '"docs_example.cli"' in init
        assert '"docs_example.api"' not in init
        assert "params_json" not in (root / "README.md").read_text()
    else:
        assert "DOCS_EXAMPLE_BASE_URL" in docs
        assert (root / "docs_example/api/api_client_base.py").is_file()
