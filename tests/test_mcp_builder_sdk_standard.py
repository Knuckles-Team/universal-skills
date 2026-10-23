"""A scaffolded connector meets every SDK centralized-capability rule.

Each test scaffolds a demo connector and asserts one US-MCP-BUILDER row. Where a
rule is a prohibition, the test also plants the violation and proves the
generated contract check reports it.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1] / "universal_skills/agent-tools/mcp-builder"
SCRIPTS = SKILL / "scripts"
GENERATION_DATE = "2026-10-22"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _scaffold(tmp_path_factory, name: str, types: str) -> Path:
    out = tmp_path_factory.mktemp(name.replace("-", "_"))
    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "scaffold_package.py"),
            name,
            "--type",
            types,
            "--output-dir",
            str(out),
            "--generation-date",
            GENERATION_DATE,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return out / name


@pytest.fixture(scope="module")
def checker():
    return _load("check_connector_contract")


@pytest.fixture(scope="module")
def api_project(tmp_path_factory) -> Path:
    return _scaffold(tmp_path_factory, "demo-conn", "api_client,mcp")


@pytest.fixture(scope="module")
def graphql_project(tmp_path_factory) -> Path:
    return _scaffold(tmp_path_factory, "demo-graph", "api_client,graphql,mcp")


@pytest.fixture(scope="module")
def cli_project(tmp_path_factory) -> Path:
    return _scaffold(tmp_path_factory, "demo-cli", "cli,mcp")


@pytest.fixture
def scratch(api_project, tmp_path) -> Path:
    """A throwaway copy so a test can plant a violation."""
    copy = tmp_path / "demo-conn"
    subprocess.run(["cp", "-r", str(api_project), str(copy)], check=True)
    return copy


def _pyproject(root: Path) -> dict:
    return tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))


def _python(root: Path, package: str) -> dict[Path, str]:
    return {
        path: path.read_text(encoding="utf-8")
        for path in (root / package).rglob("*.py")
    }


def _violations(checker, root: Path, package: str, row: str) -> list[str]:
    return [v for v in checker.check_sdk_rules(root, package) if f"-{row}]" in v]


@pytest.mark.parametrize("fixture", ["api_project", "graphql_project", "cli_project"])
def test_every_variant_passes_the_generated_contract(checker, request, fixture):
    root = request.getfixturevalue(fixture)
    package = root.name.replace("-", "_")
    assert checker.check_project(root, package) == []
    assert checker.check_sdk_rules(root, package) == []


# --- US-MCP-BUILDER-R001: governed HTTP client, SDK retries --------------------


def test_http_uses_the_sdk_governed_client_and_pins_no_http_library(
    checker, api_project, scratch
):
    project = _pyproject(api_project)["project"]
    pinned = {
        re.split(r"[<>=!~\[; ]", value)[0].lower()
        for value in project["dependencies"]
        + [v for values in project["optional-dependencies"].values() for v in values]
    }
    assert not pinned & {"requests", "httpx"}
    client = (api_project / "demo_conn/api/api_client_base.py").read_text()
    assert "from agent_connector_sdk.http.client import create_http_client" in client
    assert "requests" not in client.replace("requests without", "")
    # A planted own client and an own requests pin are both reported.
    (scratch / "demo_conn/api/own.py").write_text(
        "import requests\nimport httpx\nc = httpx.Client()\nmax_retries = 3\n"
    )
    toml = scratch / "pyproject.toml"
    toml.write_text(
        toml.read_text().replace(
            "[project.optional-dependencies]",
            '[project.optional-dependencies]\nhttp = ["requests>=2"]',
        )
    )
    found = _violations(checker, scratch, "demo_conn", "R001")
    assert any("imports requests" in v for v in found)
    assert any("own httpx client" in v for v in found)
    assert any("retry policy" in v for v in found)
    assert any("pins requests" in v for v in found)


# --- US-MCP-BUILDER-R002: resolve_tls_profile, verification never disabled -----


def test_tls_comes_from_the_resolved_profile(checker, api_project, scratch):
    auth = (api_project / "demo_conn/auth.py").read_text()
    assert "from agent_connector_sdk.tls.resolve import resolve_tls_profile" in auth
    assert "tls_profile=tls" in auth
    for text in _python(api_project, "demo_conn").values():
        assert not re.search(r"verify\s*=\s*False|disable_warnings|CERT_NONE", text)
    (scratch / "demo_conn/api/tls.py").write_text(
        "import ssl\nimport urllib3\n"
        "ctx = ssl.create_default_context()\nurllib3.disable_warnings()\n"
        "s.get(u, verify=False)\n"
    )
    found = _violations(checker, scratch, "demo_conn", "R002")
    assert len(found) >= 3


# --- US-MCP-BUILDER-R003: credential references through the SDK ----------------


def test_secrets_resolve_through_the_sdk(checker, api_project, scratch):
    auth = (api_project / "demo_conn/auth.py").read_text()
    assert "bearer_auth(setting(" in auth and "_TOKEN_REF" in auth
    env = (api_project / ".env.example").read_text()
    assert "env://" in env or "openbao://" in env or "TOKEN_REF" in env
    (scratch / "demo_conn/secrets.py").write_text(
        "import os\n"
        'def ref(v):\n    return v.startswith(("env://", "openbao://"))\n'
        'TOKEN = os.environ["DEMO_API_TOKEN"]\n'
    )
    found = _violations(checker, scratch, "demo_conn", "R003")
    assert any("by hand" in v for v in found)
    assert any("plain environment variable" in v for v in found)


# --- US-MCP-BUILDER-R004: optional dependencies only through SDK extras --------


def test_graphql_uses_the_sdk_extra_and_helpers(checker, graphql_project, scratch):
    project = _pyproject(graphql_project)["project"]
    assert project["dependencies"] == [
        "agent-connector-sdk[mcp,graphql]>=0.3.11,<1.0.0"
    ]
    assert project["optional-dependencies"]["graphql"] == [
        "agent-connector-sdk[graphql]>=0.3.11,<1.0.0"
    ]
    assert "gql" not in (graphql_project / "pyproject.toml").read_text().replace(
        "graphql", ""
    )
    module = next((graphql_project / "demo_graph").glob("*_gql.py")).read_text()
    assert "from agent_connector_sdk.mcp.graphql import" in module
    assert "import gql" not in module and "from gql" not in module
    toml = scratch / "pyproject.toml"
    toml.write_text(
        toml.read_text().replace(
            "[project.optional-dependencies]",
            "[project.optional-dependencies]\n"
            'db = ["psycopg[binary]>=3", "pymongo>=4"]\nq = ["gql[requests]>=4"]',
        )
    )
    found = _violations(checker, scratch, "demo_conn", "R004")
    assert len(found) == 3


# --- US-MCP-BUILDER-R005: fleet name declared once -----------------------------


def test_fleet_name_is_declared_once_and_never_spelled(checker, api_project, scratch):
    entry = _pyproject(api_project)["project"]["entry-points"][
        "agent_connector_sdk.connector"
    ]
    assert entry == {"demo-conn-mcp": "demo_conn"}
    server = (api_project / "demo_conn/mcp_server.py").read_text()
    assert "ConnectorContent.for_package(" in server
    ingest = (api_project / "demo_conn/kg_ingest.py").read_text()
    assert "IngestBinding.for_package(__name__," in ingest
    for text in _python(api_project, "demo_conn").values():
        assert not re.search(r"connector\s*=\s*[\"']", text)
        assert '"demo-conn-mcp"' not in text
    manifest = (api_project / "demo_conn/connector_manifest.yml").read_text()
    assert '"connector": "demo-conn-mcp"' in manifest
    # A literal name and a second entry point are both rejected.
    (scratch / "demo_conn/lit.py").write_text(
        'B = IngestBinding(connector="demo-conn", stream="s")\n'
    )
    assert _violations(checker, scratch, "demo_conn", "R005")
    toml = scratch / "pyproject.toml"
    toml.write_text(
        toml.read_text().replace(
            'demo-conn-mcp = "demo_conn"\n',
            'demo-conn-mcp = "demo_conn"\nother = "demo_conn"\n',
        )
    )
    assert any(
        "exactly one" in v for v in _violations(checker, scratch, "demo_conn", "R005")
    )


def test_fleet_name_override_flows_to_every_declaration(tmp_path):
    out = tmp_path
    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "scaffold_package.py"),
            "plain-svc",
            "--fleet-name",
            "plain-mcp",
            "--output-dir",
            str(out),
            "--generation-date",
            GENERATION_DATE,
        ],
        check=True,
        capture_output=True,
    )
    root = out / "plain-svc"
    assert _pyproject(root)["project"]["entry-points"][
        "agent_connector_sdk.connector"
    ] == {"plain-mcp": "plain_svc"}
    assert (
        '"connector": "plain-mcp"'
        in (root / "plain_svc/connector_manifest.yml").read_text()
    )
    assert (
        "plain-svc"
        not in (root / "plain_svc/connectors/tool_schema_fingerprints.json").read_text()
    )


# --- US-MCP-BUILDER-R006: tools, bootstrap, agent contract, specs --------------


def test_surface_bootstrap_agent_contract_and_specs(checker, api_project, scratch):
    server = (api_project / "demo_conn/mcp_server.py").read_text()
    assert "register_tool_surface(" in server
    assert "client_cls=ApiClientSystem" in server
    for text in _python(api_project, "demo_conn").values():
        assert "params_json" not in text
    bootstrap = (api_project / "scripts/bootstrap.sh").read_text()
    assert not re.search(r"(curl|wget)[^\n|]*\|\s*(ba|z)?sh", bootstrap)
    agents = (api_project / "AGENTS.md").read_text()
    assert "<!-- agent-contract:start -->" in agents
    assert "<!-- agent-contract:end -->" in agents
    specs = [p for p in (api_project / "specs").iterdir() if p.is_dir()]
    assert specs
    spec = specs[0]
    for name in ("spec.md", "requirements.md", "plan.md", "test-spec.md", "tasks.md"):
        assert (spec / name).is_file()
    assert "tests/" in (spec / "test-spec.md").read_text()
    # A piped installer and a missing spec file are reported.
    script = scratch / "scripts/bootstrap.sh"
    script.write_text(script.read_text() + "\ncurl -LsSf https://x.invalid/i.sh | sh\n")
    (scratch / "specs" / spec.name / "plan.md").unlink()
    found = _violations(checker, scratch, "demo_conn", "R006")
    assert any("pipes a network response" in v for v in found)
    assert any("plan.md" in v for v in found)


# --- US-MCP-BUILDER-R007: version bookkeeping ----------------------------------


def test_version_is_single_sourced_and_bumpversion_tracks_every_pin(
    checker, api_project, scratch
):
    assert "current_version = 0.1.0" in (api_project / ".bumpversion.cfg").read_text()
    version_files = [
        path
        for path, text in _python(api_project, "demo_conn").items()
        if re.search(r"^__version__\s*=", text, re.M)
    ]
    assert [p.name for p in version_files] == ["_version.py"]
    cfg = (api_project / ".bumpversion.cfg").read_text()
    assert "demo_conn/_version.py" in cfg
    assert "[bumpversion:file(dockerpin):docker/Dockerfile]" in cfg
    assert "demo-conn[mcp]==0.1.0" in (api_project / "docker/Dockerfile").read_text()
    # A stale file entry (systems-manager), a drifted image pin (ciso-assistant) and
    # a second __version__ are all reported.
    (scratch / ".bumpversion.cfg").write_text(
        (scratch / ".bumpversion.cfg").read_text()
        + "\n[bumpversion:file:demo_conn/agent_server.py]\nsearch = x\nreplace = y\n"
    )
    docker = scratch / "docker/Dockerfile"
    docker.write_text(docker.read_text().replace("==0.1.0", "==0.1.9"))
    (scratch / "demo_conn/mcp_server.py").write_text('__version__ = "0.1.0"\n')
    found = _violations(checker, scratch, "demo_conn", "R007")
    assert any("agent_server.py, which does not exist" in v for v in found)
    assert any("pins 0.1.9" in v for v in found)
    assert any("assigns __version__" in v for v in found)


# --- US-MCP-BUILDER-R008: pipelines hooks in strict mode -----------------------


def test_precommit_enables_the_strict_hooks(checker, api_project, scratch):
    config = (api_project / ".pre-commit-config.yaml").read_text()
    assert re.search(r"- id: connector-name\n\s+args: \[--strict\]", config)
    # sdk-conformance is not yet published by pipelines: it ships pending, in strict mode.
    assert "# PENDING" in config
    assert re.search(r"# - id: sdk-conformance\n\s+#\s+args: \[--strict\]", config)
    assert "entry: python -m demo_conn.mcp_server --help" in config
    assert "uv run" not in config.split("check-cli-help")[1].split("- id: pytest")[0]
    # Publishing the hook flips the template to a live strict entry.
    quality = _load("quality_templates")
    quality.SDK_CONFORMANCE_PUBLISHED = True
    live = quality.render_precommit_config("demo_conn")
    assert re.search(r"(?m)^  - id: sdk-conformance\n    args: \[--strict\]", live)
    cfg = scratch / ".pre-commit-config.yaml"
    cfg.write_text(
        cfg.read_text()
        .replace("    args: [--strict]\n  # PENDING", "  # PENDING", 1)
        .replace(
            "entry: python -m demo_conn.mcp_server --help",
            "entry: uv run python -m demo_conn.mcp_server --help",
        )
    )
    found = _violations(checker, scratch, "demo_conn", "R008")
    assert any("connector-name" in v for v in found)
    assert any("plain install" in v for v in found)


# --- US-MCP-BUILDER-R009: the skill lists every rule with its row id -----------


SDK_ROWS = [
    "R001",
    "R008",
    "R009",
    "R016",
    "R030",
    "R040",
]


def test_skill_checklist_names_every_rule_and_sdk_row():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    section = text.split("## SDK conformance checklist", 1)[1].split("\n## ", 1)[0]
    for row in range(1, 9):
        assert f"US-MCP-BUILDER-R00{row}" in section
    for row in SDK_ROWS:
        assert f"SDK-CENTRALIZED-CAPABILITIES-{row}" in section
    assert "agent_connector_sdk.connector" in section
    assert "for_package" in section
    assert "sdk-conformance" in section and "pending" in section.lower()
