"""The connector scaffold emits the minimal SDK-centralized tree (US-MCP-BUILDER-R011).

The generated package is installed (editable, no dependencies) into a throwaway
virtual environment that shares this interpreter's packages, so the SDK builds,
serves and tests it exactly as it would a released connector. Requires
agent-connector-sdk>=0.5.1, `uv` and the pipelines hooks.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import sysconfig
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
    "demo_mcp/api_client.py",
    "demo_mcp/auth.py",
    "demo_mcp/connector_sources.py",
    "demo_mcp/ontology/demo.ttl",
    "demo_mcp/prompts/demo-operator.json",
    "demo_mcp/skills/demo-operations/SKILL.md",
    "pyproject.toml",
    "specs/README.md",
    "specs/demo-mcp/plan.md",
    "specs/demo-mcp/requirements.md",
    "specs/demo-mcp/spec.md",
    "specs/demo-mcp/status.json",
    "specs/demo-mcp/tasks.md",
    "specs/demo-mcp/test-spec.md",
    "tests/test_api_client.py",
}
FORBIDDEN = (
    "mcp_server.py",
    "tools.py",
    "Dockerfile",
    "_version.py",
    ".bumpversion.cfg",
    "certification.json",
    "connector.shacl.ttl",
    "mcp_config.json",
    "conftest.py",
    "kg_ingest.py",
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
    assert project["entry-points"]["agent_connector_sdk.connector"] == {
        FLEET: "demo_mcp:connector"
    }
    assert project["scripts"] == {FLEET: "agent_connector_sdk.cli:serve"}
    assert project["dependencies"] == ["agent-connector-sdk[mcp]>=0.5.1,<0.6"]
    for path, text in _files(connector).items():
        if path != "pyproject.toml" and path.endswith(".py"):
            assert "__version__" not in text.decode(), path
            assert FLEET not in text.decode(), path


# spec: US-MCP-BUILDER-R011.4
def test_workflows_call_the_shared_pipelines_for_pypi_and_docker(connector):
    release = (connector / ".github/workflows/pipeline.yml").read_text()
    assert "connector: true" in release
    assert "render_connector: true" in release
    assert "pipelines/.github/workflows/python_pipeline.yml@main" in release
    assert "pipelines/.github/workflows/container_pipeline.yml@main" in release
    pr = (connector / ".github/workflows/connector-pr.yml").read_text()
    assert "connector_pr_pipeline.yml@main" in pr




PROBE = """
import json
from agent_connector_sdk.connector import build_server
from agent_connector_sdk.ingest.live_declaration import load_declaration
from agent_connector_sdk.mcp.tool_surface import registered_tools
import asyncio
from fastmcp import Client

_, mcp = build_server("demo_mcp", command_args=["--transport", "stdio"])
tools = {
    name: {
        "read": bool(t.annotations.read_only_hint),
        "destructive": bool(t.annotations.destructive_hint),
        "args": sorted(t.parameters.get("properties", {})),
    }
    for name, t in registered_tools(mcp).items()
}

async def listing():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        resources = await client.list_resources()
        return (
            [(p.name, p.title, sorted((p.meta or {}).keys())) for p in prompts],
            sorted(str(r.uri) for r in resources),
        )

prompts, resources = asyncio.run(listing())
declaration = load_declaration("demo_mcp")
print(json.dumps({
    "tools": tools,
    "prompts": prompts,
    "resources": resources,
    "sources": [s.source_id for s in declaration.sources],
    "connector": declaration.connector,
}))
"""


@pytest.fixture(scope="module")
def installed(connector, tmp_path_factory):
    """A throwaway environment that adds this interpreter's packages to its path, with the connector installed."""
    pytest.importorskip("agent_connector_sdk.testing.plugin")  # 0.5.0
    pytest.importorskip("agent_connector_sdk.auth.declare")  # 0.5.1
    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("uv is not installed")
    env = tmp_path_factory.mktemp("venv")
    subprocess.run([sys.executable, "-m", "venv", str(env)], check=True)
    python = env / "bin" / "python"
    site = Path(subprocess.check_output([str(python), "-c", "import sysconfig;print(sysconfig.get_path('purelib'))"], text=True).strip())
    (site / "shared.pth").write_text(sysconfig.get_path("purelib") + "\n", encoding="utf-8")
    subprocess.run(
        [uv, "pip", "install", "--python", str(python), "--no-deps", "-q", "-e", str(connector)],
        check=True,
        capture_output=True,
    )
    return python


@pytest.fixture(scope="module")
def probe(installed, connector):
    run = subprocess.run(
        [str(installed), "-c", PROBE], cwd=connector, capture_output=True, text=True
    )
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout.splitlines()[-1])


# spec: US-MCP-BUILDER-R011.5
def test_one_tool_per_operation_with_risk_annotations(probe):
    tools = probe["tools"]
    assert set(tools) == {f"demo_{op}_item" for op in ("get", "create", "update", "delete")}
    for name, tool in tools.items():
        assert "action" not in tool["args"] and "params_json" not in tool["args"], name
    assert tools["demo_get_item"]["read"] and not tools["demo_get_item"]["destructive"]
    assert not tools["demo_create_item"]["read"]
    assert tools["demo_delete_item"]["destructive"]


# spec: US-MCP-BUILDER-R011.6
def test_sources_load_as_typed_declaration_with_no_manifest_file(probe, connector):
    assert probe["sources"] == ["demo_items"]
    assert probe["connector"] == FLEET
    assert "connector://resources" in probe["resources"]
    assert not list(connector.rglob("connector_manifest.yml"))
    source = (connector / "demo_mcp/connector_sources.py").read_text()
    assert "def declaration" not in source


# spec: US-MCP-BUILDER-R011.7
def test_prompt_skill_and_ontology_are_served_over_mcp(probe):
    served = {name: (title, meta_keys) for name, title, meta_keys in probe["prompts"]}
    title, meta_keys = served["demo-operator"]
    assert title == "Demo operator"
    assert meta_keys
    uris = probe["resources"]
    assert "ontology://demo-mcp/demo.ttl" in uris
    assert any(u.startswith("skill://") for u in uris)


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
    shutil.copytree(connector, repo)
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    for cmd in (["init", "-q", "-b", "main"], ["add", "--", "."], ["commit", "-q", "-m", "scaffold"]):
        subprocess.run(["git", *cmd], cwd=repo, check=True, env=env, capture_output=True)
    return repo


def _hooks(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "pipelines_hooks.cli", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


# spec: US-MCP-BUILDER-R011.9
def test_pipelines_connector_gates_pass(connector, tmp_path):
    pytest.importorskip("pipelines_hooks")
    repo = _git_repo(connector, tmp_path)
    for gate in (("connector-name", "--root", str(repo), "--strict"), ("connector-standard",)):
        run = _hooks(*gate, cwd=repo)
        assert run.returncode == 0, gate[0] + run.stdout + run.stderr


# The epistemic-graph revision whose ontology the graph check composes. Move it deliberately.
EG_REF = "4a1780082fbe6bf7756718316e4997ec23712eb8"
EG_URL = os.environ.get("EPISTEMIC_GRAPH_URL", "https://github.com/Knuckles-Team/epistemic-graph")


def _core_ontology(base: Path) -> Path:
    """A repository holding the core ontology files at the pinned revision."""
    local = os.environ.get("EPISTEMIC_GRAPH_REPO")
    if local and Path(local).is_dir():
        return Path(local)
    repo = base / "epistemic-graph"
    repo.mkdir()
    steps = (
        ["init", "-q", "-b", "main"],
        ["remote", "add", "origin", EG_URL],
        ["sparse-checkout", "set", "crates/eg-core/ontology"],
        ["fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", EG_REF],
        ["checkout", "-q", "-B", "main", "FETCH_HEAD"],
    )
    for step in steps:
        done = subprocess.run(["git", *step], cwd=repo, capture_output=True, text=True)
        if done.returncode != 0:
            pytest.fail(f"cannot fetch the core ontology at {EG_REF}: {done.stderr}")
    return repo


# spec: US-MCP-BUILDER-R011.10
def test_ontology_graph_check_passes_against_the_core_ontology(connector, tmp_path):
    pytest.importorskip("pipelines_hooks")
    pytest.importorskip("rdflib")
    eg = _core_ontology(tmp_path)
    fleet = tmp_path / "fleet"
    fleet.mkdir()
    _git_repo(connector, fleet)
    out = tmp_path / "result.json"
    _hooks(
        "connector-ontology-map", "graph-check", "--fleet", str(fleet), "--eg-repo", str(eg),
        "--ref", "main", "--json", str(out),
    )
    result = json.loads(out.read_text())
    mine = [f for f in result["findings"] if FLEET in json.dumps(f)]
    assert not mine, mine


# spec: US-MCP-BUILDER-R011.11
def test_generated_package_passes_the_sdk_conformance_plugin(installed, connector):
    run = subprocess.run(
        [str(installed), "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA"],
        cwd=connector,
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert run.stdout.count("connector_conformance::") >= 9, run.stdout
    assert not list(connector.rglob("conftest.py"))


# spec: US-MCP-BUILDER-R011.12
def test_client_is_one_sdk_auth_declaration_with_no_own_transport(connector):
    auth = (connector / "demo_mcp/auth.py").read_text()
    assert "client_factory(" in auth and "from agent_connector_sdk.auth.declare import" in auth
    assert "delegation=True" in auth and "tls=" in auth
    for path, text in _files(connector).items():
        if path.endswith(".py") and "__pycache__" not in path:
            body = text.decode()
            for banned in ("import requests", "import httpx", "verify=False", "ssl.create_default_context", "threading.local"):
                assert banned not in body, (path, banned)


# spec: US-MCP-BUILDER-R011.13
def test_optional_dependencies_are_sdk_extras_only(connector):
    project = tomllib.loads((connector / "pyproject.toml").read_text())["project"]
    assert project["dependencies"] == ["agent-connector-sdk[mcp]>=0.5.1,<0.6"]
    assert "optional-dependencies" not in project
    assert set(project["entry-points"]) == {"agent_connector_sdk.connector"}
