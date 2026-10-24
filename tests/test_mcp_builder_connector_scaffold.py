"""The connector scaffold emits the minimal SDK-centralized tree (US-MCP-BUILDER-R011).

Tests that need the SDK, rdflib or the pipelines hooks skip when those are not
installed; the SDK conformance plugin test skips below agent-connector-sdk 0.5.0.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts/scaffold_connector.py"
)
FLEET = "demo-mcp"
EXPECTED = {
    ".github/workflows/connector-pr.yml",
    ".github/workflows/pipeline.yml",
    ".pre-commit-config.yaml",
    "AGENTS.md",
    "README.md",
    "demo_mcp/__init__.py",
    "demo_mcp/__main__.py",
    "demo_mcp/client.py",
    "demo_mcp/ontology/demo.ttl",
    "demo_mcp/prompts/demo-operator.json",
    "demo_mcp/skills/demo-operations/SKILL.md",
    "demo_mcp/tools.py",
    "docker/Dockerfile",
    "pyproject.toml",
    "specs/README.md",
    "specs/demo-mcp/plan.md",
    "specs/demo-mcp/requirements.md",
    "specs/demo-mcp/spec.md",
    "specs/demo-mcp/status.json",
    "specs/demo-mcp/tasks.md",
    "specs/demo-mcp/test-spec.md",
    "tests/test_tools.py",
}
FORBIDDEN = (
    "mcp_server.py",
    "_version.py",
    ".bumpversion.cfg",
    "connector_sources.py",
    "certification.json",
    "connector.shacl.ttl",
    "mcp_config.json",
    "conftest.py",
    "kg_ingest.py",
    "auth.py",
    "pack.ttl",
)


def _generate(out: Path) -> Path:
    subprocess.run(
        [sys.executable, str(SCRIPT), FLEET, "--output-dir", str(out)],
        check=True,
        capture_output=True,
    )
    return out / FLEET


def _files(root: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(root)): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


@pytest.fixture(scope="module")
def connector(tmp_path_factory) -> Path:
    return _generate(tmp_path_factory.mktemp("connector"))


# spec: US-MCP-BUILDER-R011.1
def test_scaffold_emits_exactly_the_minimal_tree(connector):
    files = set(_files(connector))
    assert files == EXPECTED
    for name in FORBIDDEN:
        assert not any(f.endswith(name) for f in files), name


# spec: US-MCP-BUILDER-R011.2
def test_generation_is_deterministic(connector, tmp_path):
    again = _generate(tmp_path)
    assert _files(again) == _files(connector)


# spec: US-MCP-BUILDER-R011.3
def test_identity_and_version_live_in_pyproject_only(connector):
    data = tomllib.loads((connector / "pyproject.toml").read_text())
    project = data["project"]
    assert project["version"] == "0.1.0"
    assert "dynamic" not in project
    assert project["entry-points"]["agent_connector_sdk.connector"] == {FLEET: "demo_mcp"}
    assert project["scripts"] == {FLEET: "agent_connector_sdk.cli:serve"}
    assert project["dependencies"] == ["agent-connector-sdk[mcp]>=0.5.0,<1.0.0"]
    for path, text in _files(connector).items():
        if path != "pyproject.toml" and path.endswith(".py"):
            assert "__version__" not in text.decode(), path
            assert FLEET not in text.decode(), path


# spec: US-MCP-BUILDER-R011.4
def test_workflows_call_the_shared_pipelines_for_pypi_and_docker(connector):
    release = (connector / ".github/workflows/pipeline.yml").read_text()
    assert "pipelines/.github/workflows/python_pipeline.yml@main" in release
    assert "pipelines/.github/workflows/container_pipeline.yml@main" in release
    pr = (connector / ".github/workflows/connector-pr.yml").read_text()
    assert "connector_pr_pipeline.yml@main" in pr


@pytest.fixture(scope="module")
def served(connector):
    pytest.importorskip("fastmcp")
    pytest.importorskip("agent_connector_sdk.mcp.content")
    sys.path.insert(0, str(connector))
    try:
        import demo_mcp.tools as tools
        from fastmcp import FastMCP

        mcp = FastMCP("demo-mcp")
        tools.register_tools(mcp)
        yield mcp, tools
    finally:
        sys.path.remove(str(connector))
        for name in [m for m in sys.modules if m.startswith("demo_mcp")]:
            del sys.modules[name]


def _list(mcp):
    import asyncio

    from fastmcp import Client

    async def go():
        async with Client(mcp) as client:
            return await client.list_tools()

    return asyncio.run(go())


# spec: US-MCP-BUILDER-R011.5
def test_one_tool_per_operation_with_risk_annotations(served):
    mcp, tools = served
    listed = {t.name: t for t in _list(mcp)}
    assert set(listed) == set(tools.CLASSES)
    for name, tool in listed.items():
        assert "action" not in tool.input_schema.get("properties", {}), name
        assert "params_json" not in tool.input_schema.get("properties", {}), name
        hints = tool.annotations
        kind = tools.CLASSES[name]
        assert bool(hints.read_only_hint) == (kind == "read"), name
        assert bool(hints.destructive_hint) == (kind == "destructive"), name


# spec: US-MCP-BUILDER-R011.6
def test_sources_are_declared_in_tool_meta_and_no_manifest_file_exists(served, connector):
    from agent_connector_sdk.ingest.live_declaration import build_declaration

    mcp, _ = served
    components = [
        c for k, c in mcp.local_provider._components.items() if str(k).startswith("tool:")
    ]
    declaration = build_declaration("demo-mcp", components)
    assert [x.source_id for x in declaration.sources] == ["demo_items"]
    assert not list(connector.rglob("connector_manifest.yml"))


# spec: US-MCP-BUILDER-R011.7
def test_prompt_skill_and_ontology_are_served_over_mcp(served, connector):
    import asyncio

    from agent_connector_sdk.mcp.content import ConnectorContent, register_connector_content
    from fastmcp import Client, FastMCP

    mcp = FastMCP("content")
    content = ConnectorContent(
        connector="demo-mcp", package_root=connector / "demo_mcp", package_version="0.1.0"
    )
    result = register_connector_content(mcp, content)
    assert (result.skills, result.prompts) == (1, 1)

    async def go():
        async with Client(mcp) as client:
            return await client.list_prompts(), await client.list_resources()

    prompts, resources = asyncio.run(go())
    prompt = prompts[0]
    assert prompt.name == "demo-operator"
    assert prompt.title == "Demo operator"
    assert "system" in (prompt.meta or {}).get("fastmcp", {}).get("tags", ["system"])
    uris = {str(r.uri) for r in resources}
    assert "ontology://demo-mcp/demo.ttl" in uris


# spec: US-MCP-BUILDER-R011.8
def test_ontology_rolls_up_to_a_core_class_and_never_imports_the_parent(connector):
    rdflib = pytest.importorskip("rdflib")
    from rdflib.namespace import OWL, RDF, RDFS

    graph = rdflib.Graph().parse(connector / "demo_mcp/ontology/demo.ttl")
    assert not list(graph.triples((None, OWL.imports, None)))
    classes = set(graph.subjects(RDF.type, OWL.Class))
    assert classes
    parent = rdflib.URIRef("http://knuckles.team/kg#Concept")
    for cls in classes:
        assert (cls, RDFS.subClassOf, parent) in graph


def _git_repo(connector: Path, base: Path) -> Path:
    repo = base / FLEET
    subprocess.run(["cp", "-r", str(connector), str(repo)], check=True)
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    for cmd in (["init", "-q", "-b", "main"], ["add", "--", "."], ["commit", "-q", "-m", "scaffold"]):
        subprocess.run(["git", *cmd], cwd=repo, check=True, env=env, capture_output=True)
    return repo


# spec: US-MCP-BUILDER-R011.9
def test_pipelines_connector_gates_pass(connector, tmp_path):
    pytest.importorskip("pipelines_hooks")
    repo = _git_repo(connector, tmp_path)
    for gate in ("connector-name", "release-standard"):
        run = subprocess.run(
            [sys.executable, "-m", "pipelines_hooks.cli", gate, "--root", str(repo), "--strict"],
            capture_output=True,
            text=True,
        )
        assert run.returncode == 0, run.stdout + run.stderr


# spec: US-MCP-BUILDER-R011.10
def test_ontology_graph_check_passes_against_the_core_ontology(connector, tmp_path):
    pytest.importorskip("pipelines_hooks")
    pytest.importorskip("rdflib")
    eg = os.environ.get("EPISTEMIC_GRAPH_REPO")
    if not eg or not Path(eg).is_dir():
        pytest.skip("set EPISTEMIC_GRAPH_REPO to an epistemic-graph checkout")
    fleet = tmp_path / "fleet"
    fleet.mkdir()
    _git_repo(connector, fleet)
    out = tmp_path / "result.json"
    run = subprocess.run(
        [sys.executable, "-m", "pipelines_hooks.cli", "connector-ontology-map", "graph-check",
         "--fleet", str(fleet), "--eg-repo", eg, "--ref", "main", "--json", str(out)],
        capture_output=True,
        text=True,
    )
    result = json.loads(out.read_text())
    mine = [f for f in result["findings"] if FLEET in json.dumps(f)]
    assert not mine, mine
    assert run.returncode in (0, 1)


# spec: US-MCP-BUILDER-R011.11
def test_generated_package_passes_the_sdk_conformance_plugin(connector, tmp_path):
    if importlib.util.find_spec("agent_connector_sdk") is None:
        pytest.skip("agent-connector-sdk is not installed")
    if importlib.util.find_spec("agent_connector_sdk.testing.plugin") is None:
        pytest.skip("requires agent-connector-sdk>=0.5.0 (conformance plugin)")
    run = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "agent_connector_sdk.testing.plugin", str(connector / "tests")],
        cwd=connector,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(connector)},
    )
    assert run.returncode == 0, run.stdout + run.stderr
