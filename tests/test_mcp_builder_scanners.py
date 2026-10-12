"""Generated connectors consume the shared structural scanner contract."""

import importlib.util
import hashlib
import tomllib
from pathlib import Path

import yaml


SCAFFOLD = (
    Path(__file__).parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts/scaffold_package.py"
)
PIPELINES_REV = "7b3d18d72b5622d455ece3bbe45a9482bc6e8b5e"
KISS_POLICY_SHA256 = "a6f2b9171123503522092aec416eaea7ad29ea98a26eb7283f02156c9c3d5c3a"


def _load_scaffold():
    spec = importlib.util.spec_from_file_location("_scanner_scaffold", SCAFFOLD)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _shared_hooks(config):
    repositories = yaml.safe_load(config)["repos"]
    shared = [
        repo
        for repo in repositories
        if repo["repo"] == "https://github.com/Knuckles-Team/pipelines"
    ]
    assert len(shared) == 1
    assert shared[0]["rev"] == PIPELINES_REV
    return {hook["id"]: hook for hook in shared[0]["hooks"]}


def test_scanner_hooks_consume_shared_authority():
    module = _load_scaffold()
    hooks = _shared_hooks(module.PRECOMMIT_CONFIG)
    assert {
        "scanner-versions",
        "complexity-staged",
        "complexity-census",
        "kiss-staged",
        "kiss-census",
        "dupehound-changed",
        "jscpd-differential",
        "jscpd-census",
        "import-cycles",
    } <= hooks.keys()
    assert all("entry" not in hook for hook in hooks.values())
    assert "tool.agent_utilities.scanners" not in module.PYPROJECT_TOML


def test_dependency_readiness_inherits_upstream_release_only_stage():
    hooks = _shared_hooks(_load_scaffold().PRECOMMIT_CONFIG)
    assert hooks["dependency-readiness"] == {"id": "dependency-readiness"}


def test_heavy_censuses_run_at_push_and_tests_are_real():
    module = _load_scaffold()
    hooks = _shared_hooks(module.PRECOMMIT_CONFIG)
    for name in (
        "complexity-census",
        "kiss-census",
        "jscpd-differential",
        "jscpd-census",
    ):
        assert hooks[name]["stages"] == ["pre-push"]
    local = [
        repo
        for repo in yaml.safe_load(module.PRECOMMIT_CONFIG)["repos"]
        if repo["repo"] == "local"
    ]
    tests = next(
        hook for repo in local for hook in repo["hooks"] if hook["id"] == "pytest"
    )
    assert tests["entry"] == "python -m pytest tests -q"
    assert tests["stages"] == ["pre-push"]


def test_scaffold_omits_copied_scanners_and_native_provisioning(tmp_path):
    module = _load_scaffold()
    module.scaffold("scanner-provider", output_dir=str(tmp_path))
    root = tmp_path / "scanner-provider"
    project = tomllib.loads((root / "pyproject.toml").read_text())
    assert project["tool"]["pipelines_hooks"]["stdout_writes"]["served_paths"] == [
        "scanner_provider"
    ]
    # The fleet hand-authored KISS policy from pipelines 7b3d18 is copied unchanged.
    config = root / ".config/kiss.toml"
    expected = SCAFFOLD.parent / "templates/kiss.toml"
    assert config.read_bytes() == expected.read_bytes()
    assert hashlib.sha256(config.read_bytes()).hexdigest() == KISS_POLICY_SHA256
    for relative in (
        ".cccc.toml",
        ".kiss/kiss.toml",
        ".importlinter",
        "scripts/check_scanners.py",
        "scripts/run_kiss.sh",
    ):
        assert not (root / relative).exists(), relative
    for text in (module.PRECOMMIT_CONFIG, module.SCANNER_CI_YML):
        for retired in (
            "cargo install",
            "rustup",
            "npm install",
            "check_scanners.py",
            "run_kiss.sh",
        ):
            assert retired not in text
    _shared_hooks((root / ".pre-commit-config.yaml").read_text())
