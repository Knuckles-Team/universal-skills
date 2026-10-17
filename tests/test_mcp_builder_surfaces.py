"""Selected surfaces must describe real generated artifacts."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts/scaffold_package.py"
)


def builder():
    spec = importlib.util.spec_from_file_location("surface_scaffold", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "types",
    [
        "api_client",
        "mcp",
        "api_client,mcp,unknown",
        "",
        "cli",
        "cli,mcp,graphql",
        "api_client,cli,mcp",
        "api_client,mcp,",
    ],
)
def test_unsupported_surfaces_fail_before_creating_output(tmp_path, types):
    with pytest.raises(ValueError, match="requires api_client,mcp"):
        builder().scaffold("surface-test", output_dir=str(tmp_path), pkg_types=types)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("types", ["api_client,mcp,agent", "cli,mcp,agent"])
def test_retired_agent_surface_fails_before_creating_output(tmp_path, types):
    with pytest.raises(ValueError, match="agent is retired"):
        builder().scaffold("surface-test", output_dir=str(tmp_path), pkg_types=types)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("backend", ["api_client", "cli"])
def test_selected_surface_files_and_commands(tmp_path, backend):
    module = builder()
    module.scaffold(
        "surface-test", output_dir=str(tmp_path), pkg_types=backend + ",mcp"
    )
    root = tmp_path / "surface-test"
    assert (root / "surface_test/mcp_server.py").is_file()
    for absent in (
        "surface_test/agent_server.py",
        "a2a.json",
        "docker/agent.compose.yml",
        "scripts/validate_agent.py",
        "scripts/validate_a2a_agent.py",
    ):
        assert not (root / absent).exists()
    bump = (root / ".bumpversion.cfg").read_text()
    assert "agent_server.py" not in bump
    assert "a2a.json" not in bump
    readme = (root / "README.md").read_text()
    assert "surface-test-agent" not in readme
    docker = (root / "docker/Dockerfile").read_text()
    assert "FROM mcp AS default" in docker
    assert " AS agent" not in docker

    assert (root / "surface_test/api").exists() is (backend == "api_client")
    assert (root / "surface_test/auth.py").exists() is (backend == "api_client")
    assert (root / "surface_test/cli.py").exists() is (backend == "cli")
    assert (root / "tests/test_cli.py").exists() is (backend == "cli")
    assert (root / "docs/capabilities/api.json").exists() is (backend == "api_client")
    assert (root / "docs/capabilities/mcp.json").is_file()
    if backend == "cli":
        assert not (root / "tests/test_auth.py").exists()
        assert not (root / "tests/test_api_wrapper.py").exists()
        assert not (root / "scripts/verify_api_integration.py").exists()
        assert "surface_test.cli" in (root / "surface_test/__init__.py").read_text()
        assert "surface_test.api" not in (root / "surface_test/__init__.py").read_text()
        for path in [
            root / ".env.example",
            root / "mcp_config.json",
            root / "docker/mcp.compose.yml",
        ]:
            text = path.read_text()
            assert "SURFACE_TEST_EXECUTABLE" in text
            assert "ALLOW_PLAINTEXT" not in text
            assert "BASE_URL" not in text
