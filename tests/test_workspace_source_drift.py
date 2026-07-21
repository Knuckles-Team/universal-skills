"""Tests for the uv workspace-source auto-emit + drift guard
(CONCEPT:OS-5.72-workspace-uv-sources).

Builds a small fake `[tool.uv.workspace]` root with two member packages under a
tmp_path, mirroring the real root pyproject.toml's shape (`agent-packages/agents/*`
style glob members + an `exclude`), then exercises:

* :func:`resolve_workspace_members` expands the glob correctly and skips excludes.
* :func:`sync_uv_sources` emits exactly one `{ workspace = true }` line per member,
  is idempotent, and never leaves/writes a `path = "..."` source for a member.
* :func:`find_path_source_drift` is clean after a sync, and catches a
  hand-reintroduced `path = "../sibling"` source for a workspace member — the
  exact drift shape that caused the original path-vs-member conflicts — in
  EITHER the root pyproject.toml or a member's own pyproject.toml.
* the `check_workspace_source_drift.py` CLI's `--check` exit code matches.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = (
    Path(__file__).parents[1]
    / "universal_skills"
    / "agent-tools"
    / "agent-package-builder"
    / "scripts"
)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


workspace_sources = _load("workspace_sources")


ROOT_PYPROJECT = """\
[project]
name = "fake-ecosystem"
version = "0.1.0"

[tool.uv.workspace]
members = [
    "pkgs/agents/*",
    "pkgs/solo",
]
exclude = [
    "pkgs/agents/excluded-one",
]
"""


def _member_pyproject(name: str, extra_sources: str = "") -> str:
    sources_block = f"\n[tool.uv.sources]\n{extra_sources}" if extra_sources else ""
    return f'[project]\nname = "{name}"\nversion = "0.1.0"\n{sources_block}'


def _build_fake_workspace(tmp_path: Path) -> Path:
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "pyproject.toml").write_text(ROOT_PYPROJECT, encoding="utf-8")

    agents = root / "pkgs" / "agents"
    (agents / "alpha-agent").mkdir(parents=True)
    (agents / "alpha-agent" / "pyproject.toml").write_text(
        _member_pyproject("alpha-agent"), encoding="utf-8"
    )
    (agents / "beta-agent").mkdir(parents=True)
    (agents / "beta-agent" / "pyproject.toml").write_text(
        _member_pyproject("beta-agent"), encoding="utf-8"
    )
    # Excluded by the workspace's own `exclude` glob — must never appear.
    (agents / "excluded-one").mkdir(parents=True)
    (agents / "excluded-one" / "pyproject.toml").write_text(
        _member_pyproject("excluded-one"), encoding="utf-8"
    )
    (root / "pkgs" / "solo").mkdir(parents=True)
    (root / "pkgs" / "solo" / "pyproject.toml").write_text(
        _member_pyproject("solo"), encoding="utf-8"
    )
    return root


def test_resolve_workspace_members_expands_globs_and_honors_exclude(tmp_path):
    root = _build_fake_workspace(tmp_path)
    members = workspace_sources.resolve_workspace_members(root)
    names = sorted(m.name for m in members)
    assert names == ["alpha-agent", "beta-agent", "solo"]


def test_sync_uv_sources_emits_workspace_true_for_every_member(tmp_path):
    root = _build_fake_workspace(tmp_path)
    changed = workspace_sources.sync_uv_sources(root)
    assert changed is True

    content = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert "alpha-agent = { workspace = true }" in content
    assert "beta-agent = { workspace = true }" in content
    assert "solo = { workspace = true }" in content
    sources_block = content.split("[tool.uv.sources]", 1)[1]
    assert "excluded-one" not in sources_block
    assert 'path = "' not in sources_block
    # The rest of the file (workspace members/exclude) is preserved untouched.
    assert "members = [" in content
    assert "exclude = [" in content
    assert "pkgs/agents/excluded-one" in content


def test_sync_uv_sources_is_idempotent(tmp_path):
    root = _build_fake_workspace(tmp_path)
    workspace_sources.sync_uv_sources(root)
    before = (root / "pyproject.toml").read_text(encoding="utf-8")
    changed_again = workspace_sources.sync_uv_sources(root)
    after = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert changed_again is False
    assert before == after


def test_no_drift_after_sync(tmp_path):
    root = _build_fake_workspace(tmp_path)
    workspace_sources.sync_uv_sources(root)
    findings = workspace_sources.find_path_source_drift(root)
    assert findings == []


def test_path_source_for_member_in_root_is_drift(tmp_path):
    root = _build_fake_workspace(tmp_path)
    workspace_sources.sync_uv_sources(root)
    content = (root / "pyproject.toml").read_text(encoding="utf-8")
    reintroduced = content.replace(
        "alpha-agent = { workspace = true }",
        'alpha-agent = { path = "pkgs/agents/alpha-agent" }',
    )
    (root / "pyproject.toml").write_text(reintroduced, encoding="utf-8")

    findings = workspace_sources.find_path_source_drift(root)
    assert len(findings) == 1
    assert findings[0].member_name == "alpha-agent"


def test_path_source_for_sibling_in_package_pyproject_is_drift(tmp_path):
    """The exact original bug: a package's OWN pyproject.toml declares a path
    source for a sibling that is ALSO a workspace member."""
    root = _build_fake_workspace(tmp_path)
    workspace_sources.sync_uv_sources(root)

    beta_pyproject = root / "pkgs" / "agents" / "beta-agent" / "pyproject.toml"
    beta_pyproject.write_text(
        _member_pyproject(
            "beta-agent",
            extra_sources='alpha-agent = { path = "../alpha-agent" }\n',
        ),
        encoding="utf-8",
    )

    findings = workspace_sources.find_path_source_drift(root)
    assert len(findings) == 1
    assert findings[0].member_name == "alpha-agent"
    assert findings[0].pyproject_path == beta_pyproject


def test_find_workspace_root_walks_up_from_a_member_dir(tmp_path):
    root = _build_fake_workspace(tmp_path)
    found = workspace_sources.find_workspace_root(
        root / "pkgs" / "agents" / "alpha-agent"
    )
    assert found == root


def test_cli_check_exit_code_reflects_drift(tmp_path):
    root = _build_fake_workspace(tmp_path)
    workspace_sources.sync_uv_sources(root)

    clean = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "check_workspace_source_drift.py"),
            "--root",
            str(root),
            "--check",
        ],
        capture_output=True,
        text=True,
    )
    assert clean.returncode == 0

    beta_pyproject = root / "pkgs" / "agents" / "beta-agent" / "pyproject.toml"
    beta_pyproject.write_text(
        _member_pyproject(
            "beta-agent",
            extra_sources='solo = { path = "../../solo" }\n',
        ),
        encoding="utf-8",
    )

    dirty = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "check_workspace_source_drift.py"),
            "--root",
            str(root),
            "--check",
        ],
        capture_output=True,
        text=True,
    )
    assert dirty.returncode == 1
    assert "solo" in dirty.stdout
