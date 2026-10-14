"""Build a generated site and exercise the shared Pages delivery contract offline."""

from __future__ import annotations

import ast
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import textwrap
from urllib.parse import unquote, urlsplit

import pytest
import yaml


SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)
SPEC_FILES = {
    "spec.md",
    "plan.md",
    "requirements.md",
    "tasks.md",
    "test-spec.md",
    "status.json",
}


def _run(command: list[str], root: Path, *, env: dict[str, str] | None = None) -> str:
    if command[0] == "git":
        env = dict(os.environ if env is None else env)
        # Git hooks export repository-local variables; foreign fixture repos must
        # not inherit the outer worktree's index, object directory or work tree.
        names = subprocess.check_output(
            ["git", "rev-parse", "--local-env-vars"], text=True
        ).splitlines()
        for name in names:
            env.pop(name, None)
    result = subprocess.run(
        command,
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


def test_fixture_git_commands_preserve_the_calling_repository(tmp_path, monkeypatch):
    parent = tmp_path / "parent"
    foreign = tmp_path / "fixture"
    parent.mkdir()
    foreign.mkdir()
    _run(["git", "init", "-q"], parent)
    (parent / "sentinel.txt").write_text("parent content\n")
    _run(["git", "add", "."], parent)
    commit = [
        "git",
        "-c",
        "user.name=Codex",
        "-c",
        "user.email=noreply@openai.com",
        "commit",
        "-qm",
        "Isolated fixture",
    ]
    _run(commit, parent)
    before = (
        _run(["git", "rev-parse", "HEAD"], parent),
        _run(["git", "write-tree"], parent),
    )
    monkeypatch.setenv("GIT_DIR", str(parent / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(parent))
    monkeypatch.setenv("GIT_INDEX_FILE", str(parent / ".git/index"))
    _run(["git", "init", "-q"], foreign)
    (foreign / "fixture.txt").write_text("fixture content\n")
    _run(["git", "add", "."], foreign)
    _run(commit, foreign)
    assert _run(["git", "ls-files"], foreign).splitlines() == ["fixture.txt"]
    assert (
        _run(["git", "rev-parse", "HEAD"], parent),
        _run(["git", "write-tree"], parent),
    ) == before


@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    parent = tmp_path_factory.mktemp("generated-site")
    _run(
        [
            sys.executable,
            str(SCRIPTS / "scaffold_package.py"),
            "site-contract",
            "--output-dir",
            str(parent),
        ],
        parent,
    )
    return parent / "site-contract"


def _capability(root: Path) -> tuple[Path, dict]:
    candidates = [
        path
        for path in (root / "specs").glob("*/status.json")
        if path.parent.name != "_template"
    ]
    assert len(candidates) == 1, (
        "a generated connector needs one starter capability spec"
    )
    path = candidates[0]
    return path.parent, json.loads(path.read_text())


def test_generated_capability_declares_work_without_delivery_receipts(generated):
    directory, status = _capability(generated)
    assert SPEC_FILES <= {path.name for path in directory.iterdir()}
    assert status["schema_version"] == 2
    assert (
        (directory / "spec.md").read_text().startswith("# " + status["spec_id"] + " — ")
    )
    assert status["delivery_state"] == "SPECIFIED"
    ids = status["requirement_ids"]
    assert ids and len(ids) == len(set(ids))
    assert {row["id"] for row in status["requirements"]} == set(ids)
    requirements = (directory / "requirements.md").read_text()
    for row in [status, *status["requirements"]]:
        assert row["delivery_state"] == "SPECIFIED"
        assert not row.get("landed_in")
        assert not row.get("verified_by")
    for identifier in ids:
        assert f"`{identifier}`" in requirements
    assert (generated / "docs/architecture.md").is_file()
    workflow = yaml.safe_load((generated / ".github/workflows/pages.yml").read_text())
    trigger = workflow.get("on", workflow.get(True))
    assert trigger["push"] == {"branches": ["main"]}
    assert workflow["jobs"]["publish-pages"]["with"]["spec_dashboard_enabled"] is True


OFFLINE_DASHBOARD = textwrap.dedent("""\
    import json
    from pathlib import Path
    import socket
    import sys
    import urllib.request

    def offline(*args, **kwargs):
        raise OSError("network disabled in generated-site acceptance")

    socket.socket.connect = offline
    urllib.request.urlopen = offline
    sys.path.insert(0, sys.argv[1])
    from spec_dashboard import main
    from spec_graph_load import load_repo

    root = Path(sys.argv[2]).resolve()
    assert main(['--root', str(root), '--config', '.config/spec-dashboard.json',
                 '--repository', 'Knuckles-Team/site-contract',
                 '--output', 'site/spec-delivery']) == 0
    requirements = load_repo(root)
    assert requirements
    for identifier, requirement in requirements.items():
        assert requirement.requirement_text, identifier
        assert requirement.verification_text, identifier
        assert requirement.delivery_state == 'SPECIFIED'
        assert requirement.depends_on <= requirements.keys()
    print(json.dumps({'requirements': len(requirements),
                      'dependencies': {key: sorted(row.depends_on)
                                       for key, row in requirements.items()}}))
    """)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.hrefs.extend(
                value for name, value in attrs if name == "href" and value
            )


def _links(path: Path) -> list[str]:
    parsed = Links()
    parsed.feed(path.read_text())
    return parsed.hrefs


def test_built_site_readiness_and_dashboard_preserve_canonical_evidence(generated):
    required = os.environ.get("MCP_BUILDER_REQUIRE_SITE") == "1"
    if importlib.util.find_spec("mkdocs") is None:
        if required:
            pytest.fail(
                "required site acceptance needs the existing MkDocs environment"
            )
        pytest.skip("MkDocs is not installed in this test environment")
    source = os.environ.get("PIPELINES_CONTRACT_ROOT")
    if not source:
        if required:
            pytest.fail("required site acceptance needs PIPELINES_CONTRACT_ROOT")
        pytest.skip(
            "set PIPELINES_CONTRACT_ROOT to the reviewed pinned pipeline snapshot"
        )
    pipeline = Path(source).resolve()
    root = generated
    _, status = _capability(root)
    env = dict(
        os.environ,
        GITHUB_TOKEN="",
        PYTHONDONTWRITEBYTECODE="1",
        SPEC_DELIVERY_ENABLED="true",
    )
    theme = root / ".pipeline-theme"
    _run(
        [
            sys.executable,
            str(theme / "scripts/sync_mkdocs_theme.py"),
            "check",
            "--root",
            str(root),
            "--source-root",
            str(theme),
            "--content-source",
            "docs",
        ],
        root,
        env=env,
    )
    _run([sys.executable, "-m", "mkdocs", "build", "--strict"], root, env=env)
    readiness = [sys.executable, str(pipeline / "scripts/pages_readiness.py")]
    options = [
        "--root",
        str(root),
        "--site",
        "site",
        "--content-source",
        "docs",
        "--readiness-input",
        "docs/agent-readiness.json",
        "--schema",
        "docs/agent-readiness.schema.json",
        "--readiness-manifest",
        "agent-readiness-manifest.json",
        "--mirror-manifest",
        "markdown-mirror-manifest.json",
    ]
    for operation in ("build", "tck"):
        report = json.loads(_run([*readiness, operation, *options], root, env=env))
        assert report["ok"] is True
        assert report["mirrors"] == report["entries"] > 0
    # A real temporary source commit gives canonical links a genuine revision;
    # it contains no Spec: delivery trailers or verification receipts.
    _run(["git", "init", "-q"], root)
    _run(["git", "add", "."], root)
    _run(
        [
            "git",
            "-c",
            "user.name=Codex",
            "-c",
            "user.email=noreply@openai.com",
            "commit",
            "-qm",
            "Generated site acceptance fixture",
        ],
        root,
    )
    revision = _run(["git", "rev-parse", "HEAD"], root).strip()
    gates = (
        "import sys; sys.path.insert(0, sys.argv[1]); "
        "from pipelines_hooks.specs import standard, status, decomposition; "
        "results = [gate.main(['--root', sys.argv[2]]) for gate in "
        "(standard, status, decomposition)]; assert results == [0, 0, 0], results"
    )
    _run([sys.executable, "-c", gates, str(pipeline), str(root)], root, env=env)
    _run(
        [sys.executable, "-c", OFFLINE_DASHBOARD, str(pipeline / "scripts"), str(root)],
        root,
        env=env,
    )
    snapshot = json.loads((root / "site/spec-delivery/snapshot.json").read_text())
    assert snapshot["version"] == 1
    assert snapshot["revision"] == revision
    assert snapshot["repository"] == "Knuckles-Team/site-contract"
    assert snapshot["captured_at"]
    for collection in snapshot["github"].values():
        assert collection["available"] is False
        assert collection["items"] is None
    records = snapshot["records"]
    assert {row["id"] for row in records} == {
        status["spec_id"],
        *status["requirement_ids"],
    }
    assert all(
        row["delivery_state"] == "SPECIFIED" and row["done"] is False for row in records
    )
    assert all(not row["landed_in"] and not row["verified_by"] for row in records)
    requirements = [row for row in records if row["kind"] == "requirement"]
    assert all(row["definition"] and row["definition_line"] > 0 for row in requirements)
    spec = next(row for row in records if row["kind"] == "spec")
    assert spec["component"] != "Unassigned"
    assert spec["plan_diagrams"]
    assert {row["role"] for row in spec["code_refs"]} >= {"implementation", "test"}
    for reference in spec["code_refs"]:
        assert reference["url"], reference
        if reference["repository"] == snapshot["repository"]:
            path = unquote(
                urlsplit(reference["url"]).path.split(f"/blob/{revision}/", 1)[1]
            )
            assert (root / path).is_file()
    assert isinstance(snapshot["spec_edges"], list)
    architecture = root / "site/architecture/index.html"
    assert architecture.is_file()
    home_links = _links(root / "site/index.html")
    assert any("architecture/" in link for link in home_links)
    assert any("spec-delivery/" in link for link in home_links)
    dashboard = root / "site/spec-delivery/index.html"
    links = _links(dashboard)
    assert "architecture.mmd" in links
    assert "snapshot.json" in links
    graph = (root / "site/spec-delivery/architecture.mmd").read_text()
    assert status["spec_id"] in graph
    assert "No documented records" not in dashboard.read_text()


def test_declared_relationships_do_not_infer_dependencies_or_delivery(
    generated, tmp_path
):
    source = os.environ.get("PIPELINES_CONTRACT_ROOT")
    if not source:
        if os.environ.get("MCP_BUILDER_REQUIRE_SITE") == "1":
            pytest.fail(
                "required relationship acceptance needs PIPELINES_CONTRACT_ROOT"
            )
        pytest.skip(
            "set PIPELINES_CONTRACT_ROOT to the reviewed pinned pipeline snapshot"
        )
    original, status = _capability(generated)
    root = tmp_path / "relationship-fixture"
    first = root / "specs" / original.name
    second = root / "specs" / "related-capability"
    first.mkdir(parents=True)
    second.mkdir()
    related_id = "CONN-RELATED-CAPABILITY"
    for path in original.iterdir():
        if path.is_file():
            first.joinpath(path.name).write_text(path.read_text())
            second.joinpath(path.name).write_text(
                path.read_text().replace(status["spec_id"], related_id)
            )
    config = generated / ".config/spec-dashboard.json"
    (root / ".config").mkdir()
    (root / ".config/spec-dashboard.json").write_text(config.read_text())
    document = first / "spec.md"
    document.write_text(document.read_text() + f"\nReferences: {related_id}-R001\n")
    before = {path: path.read_bytes() for path in root.glob("specs/*/status.json")}
    code = textwrap.dedent("""\
        import json
        from pathlib import Path
        import sys

        sys.path.insert(0, sys.argv[1])
        from spec_dashboard_metadata import enrich_records
        from spec_dashboard_sources import read_records

        root = Path(sys.argv[2]).resolve()
        config = json.loads((root / '.config/spec-dashboard.json').read_text())
        snapshot = {'repository': 'Knuckles-Team/site-contract', 'revision': 'parser-fixture',
                    'records': read_records(root, config)}
        enrich_records(root, snapshot)
        assert all(row['delivery_state'] == 'SPECIFIED' and not row['done']
                   for row in snapshot['records'])
        print(json.dumps(snapshot['spec_edges']))
        """)
    command = [sys.executable, "-c", code, str(Path(source) / "scripts"), str(root)]
    references = json.loads(_run(command, root))
    assert [status["spec_id"], "references", related_id] in references
    assert not any(edge[1] == "depends on" for edge in references)
    external = (
        "https://github.com/Knuckles-Team/agent-connector-sdk/blob/"
        "5babc4cc48ad73928468b243842f219f51e2cca1/specs/SDK-CONNECTOR-CONTROL/spec.md"
    )
    document.write_text(
        document.read_text()
        + f"\nDepends-on: {related_id}-R002, [External declaration]({external})\n"
    )
    dependencies = json.loads(_run(command, root))
    assert [status["spec_id"], "depends on", related_id] in dependencies
    assert [status["spec_id"], "depends on", external] in dependencies
    assert all(path.read_bytes() == contents for path, contents in before.items())


@pytest.mark.parametrize("package_name", ["immich-mcp", "craft-api"])
def test_suffix_package_spec_mappings_resolve_generated_sources(package_name, tmp_path):
    _run(
        [
            sys.executable,
            str(SCRIPTS / "scaffold_package.py"),
            package_name,
            "--output-dir",
            str(tmp_path),
        ],
        tmp_path,
    )
    root = tmp_path / package_name
    capability, _ = _capability(root)
    documents = [*capability.glob("*.md"), root / "docs/architecture.md"]
    code_paths = []
    named_targets = set()
    for document in documents:
        text = document.read_text()
        for declaration in re.findall(r"^Code:\s*(.+)$", text, re.MULTILINE):
            for source in declaration.split():
                target = (document.parent / source.split(":", 1)[0]).resolve()
                assert target.is_file(), (document.relative_to(root), source)
                code_paths.append(target)
        for filename, function in re.findall(
            r"`(tests/[\w/.-]+\.py)(?:::([\w]+))?`", text
        ):
            target = root / filename
            assert target.is_file(), (document.relative_to(root), filename)
            if function:
                definitions = {
                    node.name
                    for node in ast.walk(ast.parse(target.read_text()))
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                assert function in definitions, (filename, function)
                named_targets.add((filename, function))
    short_name = package_name.rsplit("-", 1)[0].replace("-", "_")
    expected = f"tests/test_{short_name}_mcp_validation.py"
    assert root / expected in code_paths
    assert (expected, "test_mcp_instance_registration") in named_targets
    assert named_targets
