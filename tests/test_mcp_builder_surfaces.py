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
    "types", ["api_client", "mcp", "api_client,agent", "api_client,mcp,unknown", ""]
)
def test_unsupported_surfaces_fail_before_creating_output(tmp_path, types):
    with pytest.raises(ValueError, match="requires api_client,mcp"):
        builder().scaffold("surface-test", output_dir=str(tmp_path), pkg_types=types)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("agent", [False, True])
def test_selected_surface_files_and_commands(tmp_path, agent):
    module = builder()
    module.scaffold(
        "surface-test",
        output_dir=str(tmp_path),
        pkg_types="api_client,mcp" + (",agent" if agent else ""),
    )
    root = tmp_path / "surface-test"
    assert (root / "surface_test/mcp_server.py").is_file()
    assert (root / "surface_test/agent_server.py").exists() is agent
    assert (root / "a2a.json").exists() is agent
    assert (root / "docker/agent.compose.yml").exists() is agent
    assert (root / "scripts/validate_agent.py").exists() is agent
    assert (root / "scripts/validate_a2a_agent.py").exists() is agent
    bump = (root / ".bumpversion.cfg").read_text()
    assert ("surface_test/agent_server.py" in bump) is agent
    assert ("a2a.json" in bump) is agent
    readme = (root / "README.md").read_text()
    assert ("surface-test-agent" in readme) is agent
    docker = (root / "docker/Dockerfile").read_text()
    assert "FROM mcp AS default" in docker
    assert (" AS agent" in docker) is agent
