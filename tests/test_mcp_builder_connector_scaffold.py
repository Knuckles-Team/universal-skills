"""The connector scaffold emits the minimal SDK-centralized tree (US-MCP-BUILDER-R011).

The generated package is installed (editable, no dependencies) into a throwaway
virtual environment that shares this interpreter's packages, so the SDK builds,
serves and tests it exactly as it would a released connector. Requires
scion-sdk>=0.9.0, `uv` and the pipelines hooks.
"""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import sysconfig
import tomllib
from pathlib import Path

import pytest
import yaml

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/skills/mcp-builder/scripts/scaffold_connector.py"
)
FLEET = "demo-mcp"
EXPECTED = {
    ".github/spec-dashboard.json",
    ".github/workflows/connector-pr.yml",
    ".github/workflows/pages.yml",
    ".github/workflows/pipeline.yml",
    ".pre-commit-config.yaml",
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "demo_mcp/__init__.py",
    "demo_mcp/__main__.py",
    "demo_mcp/api_client.py",
    "demo_mcp/auth.py",
    "demo_mcp/connector_contracts.py",
    "demo_mcp/connector_sources.py",
    "demo_mcp/ontology/demo.ttl",
    "demo_mcp/prompts/demo-item-steward.json",
    "demo_mcp/prompts/demo-operator.json",
    "demo_mcp/skills/demo-mcp-development/SKILL.md",
    "demo_mcp/skills/demo-operations/SKILL.md",
    ".gitignore",
    "pages/index.md",
    "pyproject.toml",
    ".specify/memory/constitution.md",
    "specs/README.md",
    "specs/demo-mcp/plan.md",
    "specs/demo-mcp/requirements.md",
    "specs/demo-mcp/spec.md",
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


_LOCAL_REFERENCE_RE = re.compile(
    r"`(?P<path>(?:tests|demo_mcp)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*)"
    r"(?:::(?P<test>test_[A-Za-z_][A-Za-z0-9_]*))?`"
)


def _local_references(root: Path) -> list[tuple[str, str | None]]:
    """Return explicit package/test references from generated Markdown.

    The pattern intentionally requires a concrete repository-local root and a
    backtick-delimited reference. Generic command examples, URLs, and
    placeholders such as ``tests/<test>.py`` are documentation, not paths to
    validate.
    """
    refs: list[tuple[str, str | None]] = []
    for path in root.rglob("*.md"):
        for match in _LOCAL_REFERENCE_RE.finditer(path.read_text(encoding="utf-8")):
            refs.append((match.group("path"), match.group("test")))
    return refs


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
    assert project["entry-points"]["scion_sdk.connector"] == {
        FLEET: "demo_mcp:connector"
    }
    assert project["scripts"] == {FLEET: "scion_sdk.cli:serve"}
    assert project["dependencies"] == ["scion-sdk[mcp]>=0.9.0,<0.10"]
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


def test_standard_connector_delivery_contract_is_scaffolded(connector):
    """New connectors carry callers/configuration for the shared delivery policy."""
    hooks = yaml.safe_load((connector / ".pre-commit-config.yaml").read_text())
    pipeline_repo = next(
        repo for repo in hooks["repos"] if repo["repo"] == "https://github.com/Knuckles-Team/pipelines"
    )
    assert [hook["id"] for hook in pipeline_repo["hooks"]] == [
        "connector-standard",
        "secrets",
        "spec",
        "tests-fast",
        "dependency-readiness",
    ]

    pages = yaml.safe_load((connector / ".github/workflows/pages.yml").read_text())
    triggers = pages.get("on", pages.get(True))
    assert "workflow_dispatch" in triggers
    caller = pages["jobs"]["publish-pages"]
    assert caller["uses"] == "Knuckles-Team/pipelines/.github/workflows/pages_pipeline.yml@main"
    assert caller["with"] == {
        "content_source": "pages",
        "shared_theme_enabled": False,
        "spec_dashboard_enabled": True,
        "spec_dashboard_config": ".github/spec-dashboard.json",
    }
    assert json.loads((connector / ".github/spec-dashboard.json").read_text()) == {
        "version": 1,
        "sources": [{"glob": "specs/*/status.json", "kind": "spec"}],
    }
    assert (connector / "pages/index.md").is_file()

    development = (connector / "demo_mcp/skills/demo-mcp-development/SKILL.md").read_text()
    for heading in (
        "## Rapid delivery: the 5-minute contract",
        "## Setup and gates",
        "## Connector-specific checks",
        "## Delivery discipline",
    ):
        assert heading in development
    assert "dependency-readiness" in development
    assert "tests/test_api_client.py::test_each_operation_calls_its_endpoint" in development


def test_generated_local_references_bind_to_real_sources_and_tests(connector):
    """Generated Markdown names only repository-local files and real tests."""
    refs = _local_references(connector)
    assert ("tests/test_api_client.py", "test_each_operation_calls_its_endpoint") in refs
    assert ("demo_mcp/api_client.py", None) in refs
    for relative, test_name in refs:
        target = connector / relative
        assert target.is_file(), relative
        if test_name is None:
            continue
        tree = ast.parse(target.read_text(encoding="utf-8"), filename=relative)
        names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert test_name in names, f"{relative}::{test_name}"


def test_local_reference_validator_ignores_placeholders_and_commands(tmp_path):
    (tmp_path / "notes.md").write_text(
        "Use `tests/<test>.py` as a placeholder and run "
        "`scripts/sync_mkdocs_theme.py sync` from the pipelines checkout.\n",
        encoding="utf-8",
    )
    assert _local_references(tmp_path) == []


# spec: US-MCP-BUILDER-R011.1
def test_generated_pages_caller_has_a_safe_shared_theme_preflight(connector):
    """A minimal tree must not opt into a theme whose canonical assets it lacks."""
    pages = yaml.safe_load((connector / ".github/workflows/pages.yml").read_text())
    caller = pages["jobs"]["publish-pages"]
    assert caller["with"]["content_source"] == "pages"
    assert caller["with"]["shared_theme_enabled"] is False
    assert (connector / "pages/index.md").read_text().startswith("# demo-mcp")
    assert not any(path.startswith(".pipeline-theme/") for path in _files(connector))
    assert not any(
        path.startswith("pages/assets/") or path.startswith("pages/stylesheets/")
        for path in _files(connector)
    )




PROBE = """
import json
from scion_sdk.connector import build_server
from scion_sdk.ingest.live_declaration import load_declaration
from scion_sdk.mcp.tool_surface import registered_tools
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
    pytest.importorskip("scion_sdk.testing.plugin")  # 0.5.0
    pytest.importorskip("scion_sdk.auth.declare")  # 0.5.1
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
    run = _hooks("connector-name", "--root", str(repo), "--strict", cwd=repo)
    assert run.returncode == 0, run.stdout + run.stderr
    # The file and spelling parts of connector-standard. Its workflow-pinning part
    # is not run: it rejects the shared `@main` workflow references that every
    # connector uses, so no conforming connector could pass it.
    for module in ("files", "codespell"):
        done = subprocess.run(
            [sys.executable, "-c", f"import sys; from pipelines_hooks.connector import {module}; sys.exit({module}.main([]))"],
            cwd=repo,
            capture_output=True,
            text=True,
        )
        assert done.returncode == 0, module + done.stdout + done.stderr
    standard = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; from pipelines_hooks.connector import standard; sys.exit(standard.main([]))",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert standard.returncode == 0, "connector-standard" + standard.stdout + standard.stderr


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


def _call_args(call: ast.Call, fields: tuple[str, ...]) -> dict[str, ast.AST]:
    """The arguments of one declaration call by field name, positional or keyword."""
    args = dict(zip(fields, call.args, strict=False))
    args.update({k.arg: k.value for k in call.keywords if k.arg})
    return args


def _strings(node: ast.AST | None) -> tuple[str, ...]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return (node.value,)
    if isinstance(node, (ast.Tuple, ast.List)):
        return tuple(v for e in node.elts for v in _strings(e))
    return ()


def _declarations(connector: Path, rel: str = "demo_mcp/connector_contracts.py") -> dict[str, list[dict[str, ast.AST]]]:
    fields = {
        "ToolUseContract": ("task", "steps", "description"),
        "ToolStep": ("tool", "params", "result", "refusals"),
        "Refusal": ("code", "when"),
        "SurfaceLink": ("task", "tools", "prompts", "skills"),
        "DataLocation": ("name", "holds", "instance", "read_tool", "store", "route_param", "federation_key"),
        "BusinessRole": ("name", "tasks", "description"),
    }
    tree = ast.parse((connector / rel).read_text(encoding="utf-8"))
    found: dict[str, list[dict[str, ast.AST]]] = {name: [] for name in fields}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) in fields:
            found[node.func.id].append(_call_args(node, fields[node.func.id]))
    return found


# spec: US-MCP-BUILDER-R011.15
def test_contracts_links_and_locations_name_generated_surface(connector):
    api = ast.parse((connector / "demo_mcp/api_client.py").read_text(encoding="utf-8"))
    methods = {
        f.name for c in api.body if isinstance(c, ast.ClassDef) and c.name == "Api"
        for f in c.body if isinstance(f, ast.FunctionDef) and not f.name.startswith("_")
    }
    tools = {f"demo_{m}" for m in methods}
    prompts = {p.stem for p in (connector / "demo_mcp/prompts").glob("*.json")}
    skills = {
        p.parent.name for p in (connector / "demo_mcp/skills").glob("*/SKILL.md")
        if not p.parent.name.endswith("-development")
    }
    ontology = (connector / "demo_mcp/ontology/demo.ttl").read_text(encoding="utf-8")
    found = _declarations(connector)
    assert len(found["ToolUseContract"]) == 1 and found["Refusal"]
    steps = [_strings(s["tool"])[0] for s in found["ToolStep"]]
    assert steps == ["demo_get_item", "demo_create_item", "demo_update_item", "demo_delete_item"]
    assert set(steps) == tools
    assert all(_strings(s.get("result")) for s in found["ToolStep"])
    assert all(_strings(r["code"]) for r in found["Refusal"])
    links = found["SurfaceLink"]
    assert set().union(*(set(_strings(link["tools"])) for link in links)) == tools
    assert {p for link in links for p in _strings(link["prompts"])} == prompts
    assert {k for link in links for k in _strings(link["skills"])} == skills
    assert {_strings(link["task"]) for link in links} == {_strings(found["ToolUseContract"][0]["task"])}
    (location,) = found["DataLocation"]
    assert _strings(location["read_tool"])[0] in tools
    assert _strings(location["instance"]) == ("DEMO_BASE_URL",)
    for held in _strings(location["holds"]):
        assert f":{held} a owl:Class" in ontology


def _assert_prompts_are_agent_definitions(root: Path, rel: str = "demo_mcp/connector_contracts.py") -> None:
    found = _declarations(root, rel)
    step_tools = {_strings(s["tool"])[0] for s in found["ToolStep"]}
    skills = {p.parent.name for p in (root / "demo_mcp/skills").glob("*/SKILL.md")}
    locations = {_strings(loc["name"])[0] for loc in found["DataLocation"]}
    roles = {_strings(r["name"])[0] for r in found["BusinessRole"]}
    links = {
        p: (set(_strings(link["tools"])), set(_strings(link["skills"])))
        for link in found["SurfaceLink"] for p in _strings(link["prompts"])
    }
    kinds = set()
    for path in sorted((root / "demo_mcp/prompts").glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        agent = document["agent"]
        kinds.add(agent["kind"])
        assert document["title"] and document["identity"]["role"] and document["identity"]["goal"]
        directive = document["instructions"]["core_directive"]
        for name in agent["tools"] + agent["skills"]:
            assert name in directive, (path.name, name)
        assert set(agent["tools"]) <= step_tools, path.name
        assert set(agent["skills"]) <= skills, path.name
        assert set(agent["data"]["reads"]) | set(agent["data"]["writes"]) <= locations, path.name
        assert agent["guardrails"]["never"], path.name
        assert {t for t in agent["tools"] if "_delete" in t} <= set(agent["guardrails"]["approval_required"])
        assert agent["outputs"], path.name
        assert links[path.stem] == (set(agent["tools"]), set(agent["skills"])), path.name
        if agent["kind"] == "business-role":
            assert agent["business_role"] in roles, path.name
    assert kinds == {"operator", "business-role"}


# spec: US-MCP-BUILDER-R011.18
def test_generated_prompts_are_complete_agent_definitions(connector):
    _assert_prompts_are_agent_definitions(connector)


def _complete(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "complete", str(repo), "--static"], capture_output=True, text=True, check=True
    )


# spec: US-MCP-BUILDER-R011.17
def test_complete_restores_missing_surface_and_is_idempotent(tmp_path):
    repo = _generate(tmp_path)
    for gone in ("demo_mcp/prompts", "demo_mcp/skills"):
        shutil.rmtree(repo / gone)
    (repo / "demo_mcp/connector_contracts.py").unlink()
    kept = (repo / "demo_mcp/ontology/demo.ttl").read_bytes()
    first = _complete(repo).stdout.splitlines()
    assert first == sorted(line for line in first if line.startswith("added: ")) + [
        line for line in first if not line.startswith("added: ")
    ]
    assert "added: demo_mcp/connector_contracts.py" in first
    assert "added: demo_mcp/skills/demo-operations/SKILL.md" in first
    assert "added: demo_mcp/prompts/demo-operator.json" in first
    assert any(line.startswith("needs a human: ") for line in first)
    assert (repo / "demo_mcp/ontology/demo.ttl").read_bytes() == kept
    before = _files(repo)
    assert _complete(repo).stdout.strip() == "complete: nothing to add"
    assert _files(repo) == before
    _assert_prompts_are_agent_definitions(repo)


# spec: US-MCP-BUILDER-R011.17
def test_complete_never_overwrites_and_suggests_import_removal(tmp_path):
    repo = _generate(tmp_path)
    ontology = repo / "demo_mcp/ontology/demo.ttl"
    ontology.write_text(ontology.read_text() + "\n<urn:x> owl:imports <http://knuckles.team/kg> .\n")
    (repo / "demo_mcp/connector_contracts.py").unlink()
    before = {k: v for k, v in _files(repo).items()}
    report = _complete(repo).stdout.splitlines()
    assert report[0] == "added: demo_mcp/connector_contracts.py"
    assert any(line.startswith("suggest: remove owl:imports of the core ontology at demo_mcp/ontology/demo.ttl:") for line in report)
    after = _files(repo)
    for path, body in before.items():
        assert after[path] == body, path


# spec: US-MCP-BUILDER-R011.16
def test_generated_connector_passes_the_sdk_surface_self_check(installed, connector):
    pytest.importorskip("scion_sdk.surface_contracts")  # 0.9.0
    run = subprocess.run(
        [str(installed), "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA", "-k", "surface_complete"],
        cwd=connector,
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "PASSED connector_conformance::surface_complete" in run.stdout.replace("pyproject.toml::", ""), run.stdout


# spec: US-MCP-BUILDER-R011.16
def test_generated_connector_passes_the_pipelines_surface_gate(connector):
    gate = pytest.importorskip("pipelines_hooks.hygiene.connector_surface")
    if "ToolUseContract" not in Path(gate.__file__).read_text(encoding="utf-8"):
        pytest.skip("the installed pipelines gate predates the tool-use contract checks")
    run = subprocess.run(
        [sys.executable, "-m", "pipelines_hooks.cli", "connector-surface-audit", "--root", str(connector), "--strict"],
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    (record,) = json.loads(run.stdout)["connectors"]
    assert record["complete"], record["gaps"]


# spec: US-MCP-BUILDER-R011.12
def test_client_is_one_sdk_auth_declaration_with_no_own_transport(connector):
    auth = (connector / "demo_mcp/auth.py").read_text()
    assert "client_factory(" in auth and "from scion_sdk.auth.declare import" in auth
    assert "delegation=True" in auth and "tls=" in auth
    for path, text in _files(connector).items():
        if path.endswith(".py") and "__pycache__" not in path:
            body = text.decode()
            for banned in ("import requests", "import httpx", "verify=False", "ssl.create_default_context", "threading.local"):
                assert banned not in body, (path, banned)


# spec: US-MCP-BUILDER-R011.13
def test_optional_dependencies_are_sdk_extras_only(connector):
    project = tomllib.loads((connector / "pyproject.toml").read_text())["project"]
    assert project["dependencies"] == ["scion-sdk[mcp]>=0.9.0,<0.10"]
    assert "optional-dependencies" not in project
    assert set(project["entry-points"]) == {"scion_sdk.connector"}


def test_agents_md_documents_bump_first_release(connector):
    text = (connector / "AGENTS.md").read_text(encoding="utf-8")
    assert "## Release" in text
    assert f"https://pypi.org/pypi/{FLEET}/X.Y.Z/json" in text
    assert "{fleet}" not in text


# spec: US-MCP-BUILDER-R011.14
def test_connector_inherits_the_organization_constitution(connector):
    text = (connector / ".specify" / "memory" / "constitution.md").read_text(encoding="utf-8")
    assert "inherits the [organization constitution](https://github.com/Knuckles-Team/pipelines/blob/main/.specify/memory/constitution.md) version 1.0.0" in text
    assert "**Inherits**: organization constitution v1.0.0" in text
    assert "### R-II. One tool per API operation" in text
    assert "{" not in text


# --- The whole project from one command (US-MCP-BUILDER-R012, R013) ---------

WRAP_URL = "https://upstream.invalid/mcp"


def _project(out: Path, *extra: str) -> Path:
    subprocess.run(
        [sys.executable, str(SCRIPT), FLEET, "--output-dir", str(out), *extra],
        check=True,
        capture_output=True,
    )
    return out


@pytest.fixture(scope="module")
def wrapped(tmp_path_factory) -> Path:
    return _project(tmp_path_factory.mktemp("wrapped"), "--wrap-mcp", WRAP_URL, "--scope-arg", "zone_id")


# spec: US-MCP-BUILDER-R012.1
def test_wrap_project_is_deterministic(wrapped, tmp_path):
    again = _project(tmp_path, "--wrap-mcp", WRAP_URL, "--scope-arg", "zone_id")
    assert _files(again) == _files(wrapped)


# spec: US-MCP-BUILDER-R012.2
def test_wrap_mounts_the_upstream_with_governance_and_no_rest_client(wrapped):
    repo = wrapped / FLEET
    files = set(_files(repo))
    for name in ("demo_mcp/upstreams.py", "demo_mcp/governance.py", "demo_mcp/probe.py",
                 "tests/test_coverage.py", "tests/test_governance.py", "CLAUDE.md"):
        assert name in files, name
    for name in ("demo_mcp/api_client.py", "demo_mcp/auth.py", "tests/test_api_client.py"):
        assert name not in files, name
    upstreams = (repo / "demo_mcp/upstreams.py").read_text()
    assert 'kind="http"' in upstreams and "upstream.invalid" not in upstreams
    assert 'CREDENTIAL = "env://DEMO_TOKEN"' in upstreams
    governance = (repo / "demo_mcp/governance.py").read_text()
    assert "ctx_confirm_destructive" in governance and "(\"zone_id\",)" in governance
    assert "action" not in tomllib.loads((repo / "pyproject.toml").read_text())["project"]


# spec: US-MCP-BUILDER-R012.3
def test_wrapped_repo_passes_its_own_gates(wrapped, tmp_path):
    pytest.importorskip("pipelines_hooks")
    repo = _git_repo(wrapped / FLEET, tmp_path)
    venv = tmp_path / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    py = venv / "bin/python"
    site = Path(subprocess.check_output([str(py), "-c", "import sysconfig;print(sysconfig.get_path('purelib'))"], text=True).strip())
    (site / "shared.pth").write_text(sysconfig.get_path("purelib") + "\n", encoding="utf-8")
    subprocess.run(["uv", "pip", "install", "-q", "--python", str(py), "--no-deps", "-e", str(repo)], check=True)
    tests = subprocess.run(
        [str(py), "-m", "pytest", "-q", "-p", "no:cacheprovider", "-c", os.devnull, "--rootdir", str(repo), str(repo / "tests")],
        cwd=repo, capture_output=True, text=True, timeout=300,
    )
    assert tests.returncode == 0, tests.stdout[-3000:] + tests.stderr[-2000:]
    assert " passed" in tests.stdout and "skipped" not in tests.stdout
    run = _hooks("connector-name", "--root", str(repo), "--strict", cwd=repo)
    assert run.returncode == 0, run.stdout + run.stderr
    for module in ("files", "codespell", "standard"):
        done = subprocess.run(
            [sys.executable, "-c", f"import sys; from pipelines_hooks.connector import {module}; sys.exit({module}.main([]))"],
            cwd=repo, capture_output=True, text=True,
        )
        assert done.returncode == 0, module + done.stdout + done.stderr


# spec: US-MCP-BUILDER-R013.1
def test_deploy_bundle_is_emitted_beside_the_repo(wrapped):
    files = set(_files(wrapped))
    for name in (
        "images/demo-mcp/Dockerfile",
        "images/demo-mcp/.gitlab-ci.yml",
        "services/demo-mcp/k8s/manifests.yaml",
        "onboarding/demo-mcp/workspace-entry.yml",
        "onboarding/demo-mcp/arbora-connector.yml",
    ):
        assert name in files, name


# spec: US-MCP-BUILDER-R013.2
def test_deploy_bundle_holds_no_secret_value_and_installs_the_release(wrapped):
    docs = list(yaml.safe_load_all((wrapped / "services/demo-mcp/k8s/manifests.yaml").read_text()))
    kinds = [d["kind"] for d in docs]
    assert kinds == ["Deployment", "Service", "Ingress", "ExternalSecret"]
    assert not any(d["kind"] == "Secret" for d in docs)
    spec = docs[0]["spec"]["template"]["spec"]
    assert "volumes" not in spec  # no source mount
    env = {e["name"]: e["value"] for e in spec["containers"][0]["env"]}
    assert env["DEMO_UPSTREAM_URL"] == WRAP_URL and "DEMO_TOKEN" not in env
    assert docs[3]["spec"]["dataFrom"] == [{"extract": {"key": "demo-mcp"}}]
    dockerfile = (wrapped / "images/demo-mcp/Dockerfile").read_text()
    assert 'pip install --no-cache-dir "demo-mcp==${VERSION}"' in dockerfile
    assert "COPY" not in dockerfile
    entry = yaml.safe_load((wrapped / "onboarding/demo-mcp/workspace-entry.yml").read_text())
    assert entry["repository"]["url"].endswith("/demo-mcp.git")
    arbora = json.loads((wrapped / "onboarding/demo-mcp/arbora-connector.yml").read_text().split("\n", 1)[1])
    assert arbora["server"] == "demo-mcp" and arbora["namespaces"] == "lazy"


# spec: US-MCP-BUILDER-R013.3
def test_deploy_profile_supplies_site_values(tmp_path):
    profile = tmp_path / "profile.yml"
    profile.write_text("registry: reg.test\ndomain: site.test\n")
    out = _project(tmp_path / "out", "--deploy-profile", str(profile))
    text = (out / "services/demo-mcp/k8s/manifests.yaml").read_text()
    assert "image: reg.test/demo-mcp:0.1.0" in text and "demo-mcp.site.test" in text
    bad = tmp_path / "bad.yml"
    bad.write_text("password: x\n")
    run = subprocess.run([sys.executable, str(SCRIPT), FLEET, "--output-dir", str(tmp_path / "b"), "--deploy-profile", str(bad)],
                         capture_output=True, text=True)
    assert run.returncode != 0 and "unknown deploy profile keys" in run.stderr
