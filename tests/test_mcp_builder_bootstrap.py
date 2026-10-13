"""Dependency admission must fail before hooks can use an ambient environment."""

import copy
import importlib.util
import json
import subprocess
import sys
import venv
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parents[1] / "universal_skills/agent-tools/mcp-builder/scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location(
    "connector_bootstrap", SCRIPTS / "bootstrap_environment.py"
)
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)
sources = importlib.import_module("bootstrap_sources")


@pytest.fixture
def inputs():
    bindings = {
        name: {"git": f"https://example.invalid/{name}.git", "rev": digit * 40}
        for name, digit in zip(sources.SOURCE_MODULES, "ab", strict=True)
    }
    project = {"tool": {"uv": {"sources": bindings}}}
    lock = {
        "package": [
            {
                "name": name,
                "version": "0.1.0",
                "source": {
                    "git": f"{binding['git']}?rev={binding['rev']}#{binding['rev']}"
                },
            }
            for name, binding in bindings.items()
        ]
    }
    return project, lock


@pytest.mark.parametrize("name", list(sources.SOURCE_MODULES))
def test_exact_source_pin_agrees_with_lock(inputs, name):
    project, lock = inputs
    binding = sources.source_binding(name, project, lock)
    assert binding["revision"] == project["tool"]["uv"]["sources"][name]["rev"]


@pytest.mark.parametrize("mutation", ["branch", "credentials", "http", "lock", "extra"])
def test_source_mismatch_or_unsafe_remote_is_rejected(inputs, mutation):
    project, lock = copy.deepcopy(inputs)
    source = project["tool"]["uv"]["sources"]["agent-connector-sdk"]
    if mutation == "branch":
        source["rev"] = "main"
    elif mutation == "credentials":
        source["git"] = "https://user:synthetic@example.invalid/sdk.git"
    elif mutation == "http":
        source["git"] = "http://example.invalid/sdk.git"
    elif mutation == "extra":
        source["branch"] = "main"
    else:
        lock["package"][0]["source"] = {"registry": "https://pypi.org/simple"}
    with pytest.raises(ValueError):
        sources.source_binding("agent-connector-sdk", project, lock)


@pytest.mark.parametrize(
    "field,value",
    [
        ("git", "https:///sdk.git"),
        ("git", "https://user@example.invalid/sdk.git"),
        ("git", "https://:synthetic@example.invalid/sdk.git"),
        ("git", "https://example.invalid/sdk.git?ref=main"),
        ("git", "https://example.invalid/sdk.git#main"),
        ("rev", "a" * 39),
        ("rev", "a" * 41),
        ("rev", "A" * 40),
    ],
)
def test_source_coordinates_reject_each_invalid_component(inputs, field, value):
    project, lock = copy.deepcopy(inputs)
    project["tool"]["uv"]["sources"]["agent-connector-sdk"][field] = value
    with pytest.raises(ValueError, match="credential-free HTTPS and a full commit ID"):
        sources.source_binding("agent-connector-sdk", project, lock)


@pytest.mark.parametrize("matches", [0, 2])
def test_source_binding_requires_exactly_one_matching_lock_entry(inputs, matches):
    project, lock = copy.deepcopy(inputs)
    package = lock["package"][0]
    lock["package"] = [package] * matches
    with pytest.raises(ValueError, match="differs between pyproject.toml and uv.lock"):
        sources.source_binding("agent-connector-sdk", project, lock)


@pytest.mark.parametrize("bindings", [[], [{"name": "epistemic-graph"}]])
def test_sync_forbids_builds_and_only_excludes_explicit_sources(bindings):
    check, sync = bootstrap.sync_commands(
        "uv", "3.12", bindings, root=Path("/reviewed/project")
    )
    assert check[:3] == ["uv", "lock", "--check"]
    assert "--frozen" in sync and sync[sync.index("--extra") + 1] == "test"
    for command in (check, sync):
        assert "--no-build" in command
        assert "--no-python-downloads" in command
        assert command[command.index("--project") + 1] == "/reviewed/project"
        assert command[command.index("--directory") + 1] == "/reviewed/project"
    excluded = [
        sync[index + 1]
        for index, value in enumerate(sync)
        if value == "--no-install-package"
    ]
    assert excluded == [source["name"] for source in bindings]


@pytest.fixture
def fake_prepare(tmp_path, monkeypatch):
    (tmp_path / "uv.lock").write_text("locked inputs")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "fixture"\n')
    events = []
    monkeypatch.setattr(
        bootstrap,
        "project_inputs",
        lambda root: ({"project": {"name": "fixture"}}, [], "3.12"),
    )
    monkeypatch.setattr(bootstrap, "run", lambda *args, **kwargs: "uv 0.12.21")

    def command(arguments, **kwargs):
        assert kwargs["check"] is True
        assert "PYTHONPATH" not in kwargs["env"]
        assert "VIRTUAL_ENV" not in kwargs["env"]
        events.append(arguments[1])

    monkeypatch.setenv("PYTHONPATH", "/unrelated/source")
    monkeypatch.setenv("VIRTUAL_ENV", "/unrelated/environment")
    monkeypatch.setattr(bootstrap.subprocess, "run", command)
    monkeypatch.setattr(
        bootstrap, "add_source_paths", lambda *args, **kwargs: events.append("paths")
    )
    monkeypatch.setattr(
        bootstrap,
        "inspect_environment",
        lambda *args, **kwargs: events.append("imports") or {"source_imports": {}},
    )
    monkeypatch.setattr(
        bootstrap, "export_github", lambda python: events.append("export")
    )
    return tmp_path, events


def test_exports_environment_only_after_locked_sync_and_imports(fake_prepare):
    root, events = fake_prepare
    record = bootstrap.prepare(root, github=True)
    assert events == ["lock", "sync", "paths", "imports", "export"]
    assert record["complete_wheel_installation_certified"] is False
    assert record["native_builds"] is False
    assert json.loads((root / ".ci/connector-environment.json").read_text()) == record


def test_lock_check_failure_prevents_sync_and_exports(fake_prepare, monkeypatch):
    root, events = fake_prepare

    def reject(arguments, **kwargs):
        events.append(arguments[1])
        raise subprocess.CalledProcessError(1, arguments)

    monkeypatch.setattr(bootstrap.subprocess, "run", reject)
    with pytest.raises(subprocess.CalledProcessError):
        bootstrap.prepare(root, github=True)
    assert events == ["lock"]
    assert not (root / ".ci/connector-environment.json").exists()


def test_missing_runtime_import_never_exports_success(fake_prepare, monkeypatch):
    root, events = fake_prepare

    def reject(*args, **kwargs):
        events.append("imports")
        raise ImportError("synthetic missing declared dependency")

    monkeypatch.setattr(bootstrap, "inspect_environment", reject)
    with pytest.raises(ImportError):
        bootstrap.prepare(root, github=True)
    assert events == ["lock", "sync", "paths", "imports"]
    assert not (root / ".ci/connector-environment.json").exists()


def test_symlinked_ci_workspace_is_not_modified(fake_prepare):
    root, events = fake_prepare
    elsewhere = root / "elsewhere"
    elsewhere.mkdir()
    (root / ".ci").symlink_to(elsewhere, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        bootstrap.prepare(root, github=True)
    assert not events
    assert not list(elsewhere.iterdir())


@pytest.mark.parametrize("filename", ["pyproject.toml", "uv.lock"])
def test_dependency_input_drift_prevents_exports(fake_prepare, monkeypatch, filename):
    root, events = fake_prepare

    def mutate(arguments, **kwargs):
        events.append(arguments[1])
        (root / filename).write_text("changed input")

    monkeypatch.setattr(bootstrap.subprocess, "run", mutate)
    with pytest.raises(ValueError, match="reviewed dependency inputs"):
        bootstrap.prepare(root, github=True)
    assert events == ["lock", "sync"]


def test_sync_failure_never_exposes_environment(fake_prepare, monkeypatch):
    root, events = fake_prepare

    def reject(arguments, **kwargs):
        events.append(arguments[1])
        if arguments[1] == "sync":
            raise subprocess.CalledProcessError(1, arguments)

    monkeypatch.setattr(bootstrap.subprocess, "run", reject)
    with pytest.raises(subprocess.CalledProcessError):
        bootstrap.prepare(root, github=True)
    assert events == ["lock", "sync"]


def test_competing_project_environment_cannot_redirect_lock_or_sync(
    fake_prepare, monkeypatch
):
    root, events = fake_prepare
    competing = root / "competing"
    competing.mkdir()
    (competing / "pyproject.toml").write_text('[project]\nname = "unrelated"\n')
    (competing / "uv.lock").write_text("unrelated lock")
    for name in ("UV_PROJECT", "UV_WORKING_DIR", "UV_WORKING_DIRECTORY"):
        monkeypatch.setenv(name, str(competing))
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.invalid:8080")

    def verify_selected_inputs(arguments, **kwargs):
        env = kwargs["env"]
        assert not {"UV_PROJECT", "UV_WORKING_DIR", "UV_WORKING_DIRECTORY"} & env.keys()
        selected = Path(arguments[arguments.index("--project") + 1])
        assert selected == root == Path(arguments[arguments.index("--directory") + 1])
        assert (selected / "uv.lock").read_text() == "locked inputs"
        assert env["HTTPS_PROXY"] == "http://proxy.example.invalid:8080"
        events.append(arguments[1])

    monkeypatch.setattr(bootstrap.subprocess, "run", verify_selected_inputs)
    bootstrap.prepare(root, github=True)
    assert events == ["lock", "sync", "paths", "imports", "export"]


def test_github_environment_clears_ambient_imports(tmp_path, monkeypatch):
    github_path, github_env = tmp_path / "path", tmp_path / "env"
    monkeypatch.setenv("GITHUB_PATH", str(github_path))
    monkeypatch.setenv("GITHUB_ENV", str(github_env))
    python = tmp_path / ".ci/connector-venv/bin/python"
    bootstrap.export_github(python)
    values = dict(line.split("=", 1) for line in github_env.read_text().splitlines())
    assert github_path.read_text().strip() == str(python.parent)
    assert values["GENERATED_SCHEMA_PYTHON"] == str(python)
    assert values["PYTHONPATH"] == values["PYTHONHOME"] == ""
    assert values["MCP_FLEET_REGISTRATION"] == "false"


@pytest.mark.parametrize("dirty", [" M module.py", "!! injected.py", "?? untracked.py"])
def test_existing_source_drift_is_rejected(inputs, tmp_path, monkeypatch, dirty):
    binding = sources.source_binding("agent-connector-sdk", *inputs)
    target = tmp_path / ".ci/sources" / (binding["name"] + "-" + binding["revision"])
    (target / ".git").mkdir(parents=True)
    (target / binding["module"]).mkdir()
    monkeypatch.setattr(
        sources,
        "run",
        lambda command, **kwargs: dirty if "status" in command else binding["revision"],
    )
    with pytest.raises(ValueError, match="stale, dirty or incomplete"):
        sources.checkout_source(tmp_path, binding, {})


def test_source_path_file_cannot_overwrite_symlink_target(tmp_path, monkeypatch):
    purelib = tmp_path / ".ci/connector-venv/lib/python3.12/site-packages"
    purelib.mkdir(parents=True)
    victim = tmp_path / "preserved"
    victim.write_text("original")
    (purelib / "_connector_sources.pth").symlink_to(victim)
    monkeypatch.setattr(bootstrap, "run", lambda *args, **kwargs: str(purelib))
    with pytest.raises(ValueError, match="symlink"):
        bootstrap.add_source_paths(tmp_path, Path("python"), [], env={})
    assert victim.read_text() == "original"


@pytest.fixture
def real_interpreter(tmp_path):
    """Use a real isolated Python with synthetic modules; install nothing."""
    env_root = tmp_path / ".ci/connector-venv"
    venv.EnvBuilder(with_pip=False).create(env_root)
    python = env_root / "bin/python"
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pipelines_hooks]\npackages = ["fixture_connector"]\n'
    )
    (tmp_path / "fixture_connector.py").write_text('"""Synthetic project."""\n')
    bootstrap.add_source_paths(tmp_path, python, [], env={})
    purelib = Path(
        bootstrap.run(
            [
                str(python),
                "-c",
                "import sysconfig; print(sysconfig.get_path('purelib'))",
            ],
            root=tmp_path,
            env={},
        )
    )
    for name in ("agent_connector_sdk", "epistemic_graph", "fastmcp", "mcp", "pytest"):
        (purelib / f"{name}.py").write_text('"""Synthetic runtime fixture."""\n')
    return tmp_path, python, purelib


def test_actual_interpreter_proves_project_and_private_environment_origins(
    real_interpreter,
):
    root, python, purelib = real_interpreter
    record = bootstrap.inspect_environment(
        root, python, bindings=[], sources=[], env={}
    )
    assert record["source_imports"]["fixture_connector"] == str(
        root / "fixture_connector.py"
    )
    assert record["source_imports"]["fastmcp"] == str(purelib / "fastmcp.py")


def test_actual_interpreter_rejects_dependency_outside_private_environment(
    real_interpreter,
):
    root, python, purelib = real_interpreter
    (purelib / "mcp.py").unlink()
    (purelib / "mcp.py").symlink_to(root / "fixture_connector.py")
    with pytest.raises(subprocess.CalledProcessError):
        bootstrap.inspect_environment(root, python, bindings=[], sources=[], env={})
