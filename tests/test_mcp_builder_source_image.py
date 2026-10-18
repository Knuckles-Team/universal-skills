"""Source image inputs must come from the generated checkout, including runtime data."""
from __future__ import annotations

import configparser
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "universal_skills/agent-tools/mcp-builder/scripts/scaffold_package.py"


def builder():
    spec = importlib.util.spec_from_file_location("source_image_scaffold", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_image_installs_the_published_wheel_never_source(tmp_path):
    module = builder()
    module.scaffold("unpublished-api", output_dir=str(tmp_path), pkg_types="api_client,mcp")
    root = tmp_path / "unpublished-api"
    docker = (root / "docker/Dockerfile").read_text()
    assert "pip install --only-binary :all: unpublished-api[mcp]==0.1.0" in docker
    assert '".[mcp]"' not in docker
    assert "COPY " not in docker
    assert "cargo" not in docker and "build-essential" not in docker
    assert "python:3.14-slim@sha256:" in docker
    assert "USER 10001" in docker
    assert "FROM mcp AS default" in docker
    assert "git clone" not in docker
    config = configparser.ConfigParser(interpolation=None)
    config.read(root / ".bumpversion.cfg")
    assert any("docker/Dockerfile" in name for name in config.sections())


def test_image_docs_build_from_the_published_release(tmp_path):
    builder().scaffold("unpublished-api", output_dir=str(tmp_path), pkg_types="api_client,mcp")
    root = tmp_path / "unpublished-api"
    readme = (root / "README.md").read_text()
    assert "--target mcp -t unpublished-api:<version>-mcp ." in readme
    deployment = (root / "docs/deployment.md").read_text()
    assert "pip install --only-binary :all:" in deployment
    assert "never installs the" in deployment


def test_named_source_builds_are_exempt_only_by_name(tmp_path):
    import tomllib

    builder().scaffold(
        "unpublished-api",
        output_dir=str(tmp_path),
        pkg_types="api_client,mcp",
        allow_source_build="Uptime_Kuma.API",
    )
    root = tmp_path / "unpublished-api"
    docker = (root / "docker/Dockerfile").read_text()
    assert "pip install --only-binary :all: --no-binary uptime-kuma-api unpublished-api[mcp]==0.1.0" in docker
    data = tomllib.loads((root / "pyproject.toml").read_text())
    assert data["tool"]["pipelines"]["allow-source-build"] == ["uptime-kuma-api"]


def test_default_scaffold_declares_no_source_builds(tmp_path):
    builder().scaffold("unpublished-api", output_dir=str(tmp_path), pkg_types="api_client,mcp")
    root = tmp_path / "unpublished-api"
    assert "--no-binary" not in (root / "docker/Dockerfile").read_text()
    assert "[tool.pipelines]" not in (root / "pyproject.toml").read_text()


@pytest.mark.parametrize("name", [":all:", "*", "a b"])
def test_source_build_wildcards_refused(name):
    with pytest.raises(ValueError, match="exact package names"):
        builder().source_build_names(name)


def test_parity_rejects_undeclared_no_binary(tmp_path):
    spec = importlib.util.spec_from_file_location("parity_check", SCRIPT.with_name("check_tool_parity.py"))
    parity = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parity)
    (tmp_path / "docker").mkdir()
    docker = tmp_path / "docker/Dockerfile"
    docker.write_text("RUN pip install --only-binary :all: --no-binary pyspark spark-mcp[mcp]==1.0\n")
    assert parity.dockerfile_findings(tmp_path) == [
        "docker/Dockerfile: --no-binary pyspark is not in [tool.pipelines] allow-source-build"
    ]
    (tmp_path / "pyproject.toml").write_text('[tool.pipelines]\nallow-source-build = ["pyspark"]\n')
    assert parity.dockerfile_findings(tmp_path) == []
    docker.write_text("RUN pip install --only-binary :all: --no-binary :all: spark-mcp[mcp]==1.0\n")
    assert parity.dockerfile_findings(tmp_path)


def _parity():
    spec = importlib.util.spec_from_file_location("parity_lost", SCRIPT.with_name("check_tool_parity.py"))
    parity = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parity)
    return parity


def test_parity_fails_on_previous_tools_without_successor(tmp_path):
    parity = _parity()
    previous = {"x_signals", "x_risk", "x_old_tool", "x_get_quote"}
    served = {"x_signals_alpha", "x_risk_kelly", "x_get_quote"}
    assert parity.lost_tools(previous, served, set()) == ["x_old_tool"]
    assert parity.lost_tools(previous, served, {"x_old_tool"}) == []


def test_parity_counts_a_covering_operation_tool_as_successor():
    parity = _parity()
    previous = {"x_branches", "x_branches_get", "x_search_code", "x_gone"}
    served = {"x_get_branch", "x_code_search"}
    report = [
        {"tool": "x_branches", "action": "get", "split": "x_branches_get",
         "outcome": "covered", "served_by": "x_get_branch", "reason": "table"},
        {"tool": "x_search", "action": "code", "split": "x_search_code",
         "outcome": "covered", "served_by": "x_not_served", "reason": "name"},
    ]
    covered = parity.covered_tools(report, served)
    assert covered == {"x_branches", "x_branches_get"}
    assert parity.lost_tools(previous, served, set(), covered) == ["x_gone", "x_search_code"]


def test_parity_reads_declared_retired_tools(tmp_path):
    parity = _parity()
    assert parity.declared_retired_tools(tmp_path) == set()
    (tmp_path / "pyproject.toml").write_text('[tool.pipelines]\nretired-tools = ["x_old_tool"]\n')
    assert parity.declared_retired_tools(tmp_path) == {"x_old_tool"}
