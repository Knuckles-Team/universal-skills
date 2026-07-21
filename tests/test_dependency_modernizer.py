"""Tests for the dependency-modernizer skill's ``bump_dependencies.py``.

Every test mocks the PyPI HTTP call (``_fetch_pypi_json``) — no live network
request is ever made from this suite.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest


# dependency-modernizer's only dependency, tomlkit, is deliberately not a
# declared package extra (see the skill's SKILL.md "Requirement" section), so
# it may genuinely be absent from a given environment. Skip this whole module
# rather than erroring when that is the case; every test here still runs for
# real wherever tomlkit is installed (e.g. `pip install tomlkit` first).
pytest.importorskip("tomlkit", reason="dependency-modernizer requires tomlkit")


SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "universal_skills"
    / "development"
    / "dependency-modernizer"
    / "scripts"
    / "bump_dependencies.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("_dep_modernizer_bump", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Register before exec: the module's @dataclass fields use postponed
    # (string) annotations, and dataclasses resolves those via sys.modules on
    # Python 3.14+, which requires the module to already be registered there.
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(spec.name, None)
        raise
    return module


@pytest.fixture()
def mod():
    return _load_module()


def _write(root: Path, repo_name: str, content: str) -> Path:
    repo_dir = root / repo_name
    repo_dir.mkdir(parents=True, exist_ok=True)
    pyproject = repo_dir / "pyproject.toml"
    pyproject.write_text(textwrap.dedent(content), encoding="utf-8")
    return pyproject


def _pypi_json(version: str) -> dict:
    return {"info": {"version": version}, "releases": {version: [{"yanked": False}]}}


# --------------------------------------------------------------------------- #
# Rule: a simple floor bumps
# --------------------------------------------------------------------------- #


def test_simple_floor_bumps(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "simple-repo",
        """\
        [project]
        name = "simple-repo"
        version = "0.1.0"
        dependencies = [
            "requests>=2.0.0",
        ]
        """,
    )
    with patch.object(mod, "_fetch_pypi_json", return_value=_pypi_json("2.31.0")):
        result = mod.bump_pyproject(pyproject)

    assert result.bumped == [
        {
            "section": "project.dependencies",
            "package": "requests",
            "from": "requests>=2.0.0",
            "to": "requests>=2.31.0",
        }
    ]
    assert "requests>=2.31.0" in result.new_text
    assert "requests>=2.0.0" not in result.new_text
    assert not result.skipped_member
    assert not result.skipped_cve
    assert not result.skipped_complex
    assert not result.errors


# --------------------------------------------------------------------------- #
# Rule: an upper cap drops (default), or is preserved verbatim with --keep-caps
# --------------------------------------------------------------------------- #


def test_upper_cap_drops_by_default(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "capped-repo",
        """\
        [project]
        name = "capped-repo"
        version = "0.1.0"
        dependencies = [
            "flask>=1.0.0,<2.0.0",
        ]
        """,
    )
    with patch.object(mod, "_fetch_pypi_json", return_value=_pypi_json("2.5.0")):
        result = mod.bump_pyproject(pyproject)

    assert result.bumped[0]["to"] == "flask>=2.5.0"
    assert "<2.0.0" not in result.new_text


def test_keep_caps_preserves_cap_verbatim(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "capped-keep-repo",
        """\
        [project]
        name = "capped-keep-repo"
        version = "0.1.0"
        dependencies = [
            "widgetlib>=1.0.0,<3.0.0",
        ]
        """,
    )
    with patch.object(mod, "_fetch_pypi_json", return_value=_pypi_json("2.0.0")):
        result = mod.bump_pyproject(pyproject, keep_caps=True)

    assert result.bumped[0]["to"] == "widgetlib>=2.0.0,<3.0.0"
    assert "<3.0.0" in result.new_text


# --------------------------------------------------------------------------- #
# Rule: a CVE-commented line is untouched
# --------------------------------------------------------------------------- #


def test_cve_commented_line_untouched(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "cve-repo",
        """\
        [project]
        name = "cve-repo"
        version = "0.1.0"
        dependencies = [
            "django>=3.2.0",  # CVE-2024-12345 floor, do not lower
        ]
        """,
    )
    original = pyproject.read_text(encoding="utf-8")
    with patch.object(
        mod, "_fetch_pypi_json", return_value=_pypi_json("5.0.0")
    ) as fetch:
        result = mod.bump_pyproject(pyproject)

    assert result.skipped_cve == ["django>=3.2.0"]
    assert not result.bumped
    assert not result.changed
    assert result.new_text == original  # byte-identical
    fetch.assert_not_called()  # never even asks PyPI about a CVE-pinned floor


# --------------------------------------------------------------------------- #
# Rule: a workspace/intra-repo member is skipped (auto-detected, and --skip)
# --------------------------------------------------------------------------- #


def test_workspace_member_is_skipped(mod, tmp_path):
    workspace_root = tmp_path / "workspace"
    _write(
        workspace_root,
        "sibling-pkg",
        """\
        [project]
        name = "sibling-pkg"
        version = "1.0.0"
        dependencies = []
        """,
    )
    pyproject = _write(
        workspace_root,
        "consumer-repo",
        """\
        [project]
        name = "consumer-repo"
        version = "0.1.0"
        dependencies = [
            "sibling-pkg>=1.0.0",
            "requests>=2.0.0",
        ]
        """,
    )

    members = mod.discover_workspace_members(str(workspace_root))
    assert "sibling-pkg" in members

    with patch.object(mod, "_fetch_pypi_json", return_value=_pypi_json("2.31.0")):
        result = mod.bump_pyproject(pyproject, workspace_members=members)

    assert result.skipped_member == ["sibling-pkg>=1.0.0"]
    assert result.bumped == [
        {
            "section": "project.dependencies",
            "package": "requests",
            "from": "requests>=2.0.0",
            "to": "requests>=2.31.0",
        }
    ]


def test_explicit_skip_name_is_skipped(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "skip-repo",
        """\
        [project]
        name = "skip-repo"
        version = "0.1.0"
        dependencies = [
            "internal-tool>=1.0.0",
        ]
        """,
    )
    with patch.object(
        mod, "_fetch_pypi_json", return_value=_pypi_json("9.9.9")
    ) as fetch:
        result = mod.bump_pyproject(pyproject, skip_names={"internal-tool"})

    assert result.skipped_member == ["internal-tool>=1.0.0"]
    fetch.assert_not_called()


def test_own_package_name_is_never_self_bumped(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "self-repo",
        """\
        [project]
        name = "self-repo"
        version = "0.1.0"
        dependencies = [
            "self-repo[extra]>=0.1.0",
        ]
        """,
    )
    with patch.object(
        mod, "_fetch_pypi_json", return_value=_pypi_json("9.9.9")
    ) as fetch:
        result = mod.bump_pyproject(pyproject)

    assert result.skipped_member == ["self-repo[extra]>=0.1.0"]
    fetch.assert_not_called()


# --------------------------------------------------------------------------- #
# Rule: a complex '@'/marker spec is skipped
# --------------------------------------------------------------------------- #


def test_complex_url_and_marker_specs_are_skipped(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "complex-repo",
        """\
        [project]
        name = "complex-repo"
        version = "0.1.0"
        dependencies = [
            "vendored-pkg @ git+https://example.com/org/vendored-pkg.git@main",
            "colorama>=0.4.0; sys_platform == 'win32'",
        ]
        """,
    )
    original = pyproject.read_text(encoding="utf-8")
    with patch.object(
        mod, "_fetch_pypi_json", return_value=_pypi_json("9.9.9")
    ) as fetch:
        result = mod.bump_pyproject(pyproject)

    assert sorted(result.skipped_complex) == sorted(
        [
            "vendored-pkg @ git+https://example.com/org/vendored-pkg.git@main",
            "colorama>=0.4.0; sys_platform == 'win32'",
        ]
    )
    assert not result.bumped
    assert not result.changed
    assert result.new_text == original
    fetch.assert_not_called()


# --------------------------------------------------------------------------- #
# Rule: --dry-run (default) previews only; --no-dry-run writes in place
# --------------------------------------------------------------------------- #


def test_dry_run_writes_nothing_but_reports_the_change(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "dryrun-repo",
        """\
        [project]
        name = "dryrun-repo"
        version = "0.1.0"
        dependencies = [
            "requests>=2.0.0",
        ]
        """,
    )
    original = pyproject.read_text(encoding="utf-8")

    with patch.object(mod, "_fetch_pypi_json", return_value=_pypi_json("2.31.0")):
        summary = mod.run([str(pyproject.parent)], dry_run=True)

    assert pyproject.read_text(encoding="utf-8") == original  # untouched on disk
    assert summary["dry_run"] is True
    assert summary["totals"]["bumped"] == 1
    assert summary["repos"]["dryrun-repo"]["bumped"][0]["to"] == "requests>=2.31.0"


def test_no_dry_run_writes_in_place(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "write-repo",
        """\
        [project]
        name = "write-repo"
        version = "0.1.0"
        dependencies = [
            "requests>=2.0.0",
        ]
        """,
    )

    with patch.object(mod, "_fetch_pypi_json", return_value=_pypi_json("2.31.0")):
        summary = mod.run([str(pyproject.parent)], dry_run=False)

    assert summary["dry_run"] is False
    on_disk = pyproject.read_text(encoding="utf-8")
    assert "requests>=2.31.0" in on_disk
    assert "requests>=2.0.0" not in on_disk


def test_cli_default_is_dry_run_and_commit_alone_writes(mod, tmp_path):
    """Exercises main()'s --dry-run/--commit precedence resolution directly."""
    pyproject = _write(
        tmp_path,
        "cli-repo",
        """\
        [project]
        name = "cli-repo"
        version = "0.1.0"
        dependencies = [
            "requests>=2.0.0",
        ]
        """,
    )
    original = pyproject.read_text(encoding="utf-8")

    with patch.object(mod, "_fetch_pypi_json", return_value=_pypi_json("2.31.0")):
        # No flags at all: must default to dry-run (write nothing).
        exit_code = mod.main([str(pyproject.parent)])
    assert exit_code == 0
    assert pyproject.read_text(encoding="utf-8") == original

    with patch.object(mod, "_fetch_pypi_json", return_value=_pypi_json("2.31.0")):
        # Explicit --dry-run always wins, even if --commit is also present.
        exit_code = mod.main([str(pyproject.parent), "--dry-run", "--commit"])
    assert exit_code == 0
    assert pyproject.read_text(encoding="utf-8") == original


# --------------------------------------------------------------------------- #
# Extra correctness checks: round-trip fidelity + graceful per-package errors
# --------------------------------------------------------------------------- #


def test_comments_and_formatting_survive_the_round_trip(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "roundtrip-repo",
        """\
        [project]
        name = "roundtrip-repo"
        version = "0.1.0"
        dependencies = [
            "requests>=2.0.0",  # bumped by tool
            "flask>=1.0.0",  # CVE-1111 floor
        ]

        [project.optional-dependencies]
        extra = [
            "pydantic[email]>=2.0.0",
        ]
        """,
    )

    def fake_fetch(name):
        return _pypi_json(
            {"requests": "2.31.0", "pydantic": "2.13.4"}.get(name, "9.9.9")
        )

    with patch.object(mod, "_fetch_pypi_json", side_effect=fake_fetch):
        result = mod.bump_pyproject(pyproject)

    assert "# CVE-1111 floor" in result.new_text
    assert "flask>=1.0.0" in result.new_text  # CVE line untouched
    assert "pydantic[email]>=2.13.4" in result.new_text  # extras preserved
    assert {"requests", "pydantic"} <= {c["package"] for c in result.bumped}


def test_never_touches_version_or_build_system(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "version-guard-repo",
        """\
        [build-system]
        requires = ["setuptools>=80.9.0"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "version-guard-repo"
        version = "3.2.1"
        dependencies = [
            "requests>=2.0.0",
        ]
        """,
    )
    with patch.object(mod, "_fetch_pypi_json", return_value=_pypi_json("2.31.0")):
        result = mod.bump_pyproject(pyproject)

    assert result.bumped  # sanity: the fixture did trigger a real bump
    assert 'version = "3.2.1"' in result.new_text
    assert 'requires = ["setuptools>=80.9.0"]' in result.new_text


def test_unresolvable_package_is_reported_not_fatal(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "missing-pkg-repo",
        """\
        [project]
        name = "missing-pkg-repo"
        version = "0.1.0"
        dependencies = [
            "this-package-does-not-exist-anywhere>=1.0.0",
        ]
        """,
    )
    with patch.object(mod, "_fetch_pypi_json", return_value=None):
        result = mod.bump_pyproject(pyproject)

    assert not result.bumped
    assert result.errors
    assert "this-package-does-not-exist-anywhere" in result.errors[0]


def test_unparseable_pyproject_is_a_batch_error_not_a_crash(mod, tmp_path):
    repo_dir = tmp_path / "broken-repo"
    repo_dir.mkdir()
    pyproject = repo_dir / "pyproject.toml"
    pyproject.write_text("this is [ not valid toml", encoding="utf-8")

    result = mod.bump_pyproject(pyproject)

    assert result.errors
    assert not result.bumped


def test_resolve_targets_handles_dirs_files_and_globs(mod, tmp_path):
    _write(tmp_path, "repo-a", '[project]\nname = "repo-a"\ndependencies = []\n')
    _write(tmp_path, "repo-b", '[project]\nname = "repo-b"\ndependencies = []\n')

    files, errors = mod.resolve_targets(
        [str(tmp_path / "repo-a"), str(tmp_path / "repo-b" / "pyproject.toml")]
    )
    assert {f.parent.name for f in files} == {"repo-a", "repo-b"}
    assert not errors

    glob_files, glob_errors = mod.resolve_targets([str(tmp_path) + "/repo-*"])
    assert {f.parent.name for f in glob_files} == {"repo-a", "repo-b"}
    assert not glob_errors

    missing_files, missing_errors = mod.resolve_targets(
        [str(tmp_path / "does-not-exist")]
    )
    assert not missing_files
    assert missing_errors


# --------------------------------------------------------------------------- #
# --commit: branch off main, commit, restore main
# --------------------------------------------------------------------------- #


def _init_git_repo(repo_dir: Path) -> None:
    def git(*args: str) -> None:
        subprocess.run(
            ["git", *args],
            cwd=str(repo_dir),
            check=True,
            capture_output=True,
            text=True,
        )

    git("init", "-b", "main")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "Test Runner")
    git("add", "pyproject.toml")
    git("commit", "-m", "initial commit")


def test_commit_branches_commits_and_restores_main(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "commit-repo",
        """\
        [project]
        name = "commit-repo"
        version = "0.1.0"
        dependencies = [
            "requests>=2.0.0",
        ]
        """,
    )
    repo_dir = pyproject.parent
    _init_git_repo(repo_dir)
    original_on_disk = pyproject.read_text(encoding="utf-8")

    with patch.object(mod, "_fetch_pypi_json", return_value=_pypi_json("2.31.0")):
        summary = mod.run(
            [str(repo_dir)],
            dry_run=False,
            commit=True,
            branch_prefix="chore/bump-deps-",
        )

    assert summary["totals"]["bumped"] == 1
    assert not summary["repos"]["commit-repo"]["errors"]

    branches = subprocess.run(
        ["git", "branch", "--list"],
        cwd=str(repo_dir),
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "chore/bump-deps-commit-repo" in branches

    current_branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=str(repo_dir),
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert current_branch == "main"

    # main's working tree is restored to the pre-bump content...
    assert pyproject.read_text(encoding="utf-8") == original_on_disk

    # ...while the feature branch actually carries the bumped, committed content.
    bumped_content = subprocess.run(
        ["git", "show", "chore/bump-deps-commit-repo:pyproject.toml"],
        cwd=str(repo_dir),
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "requests>=2.31.0" in bumped_content


def test_commit_skips_repo_with_no_change(mod, tmp_path):
    pyproject = _write(
        tmp_path,
        "nochange-repo",
        """\
        [project]
        name = "nochange-repo"
        version = "0.1.0"
        dependencies = [
            "django>=3.2.0",  # CVE-2024-12345 floor, do not lower
        ]
        """,
    )
    repo_dir = pyproject.parent
    _init_git_repo(repo_dir)

    with patch.object(mod, "_fetch_pypi_json", return_value=_pypi_json("5.0.0")):
        summary = mod.run(
            [str(repo_dir)],
            dry_run=False,
            commit=True,
            branch_prefix="chore/bump-deps-",
        )

    assert summary["totals"]["bumped"] == 0
    branches = subprocess.run(
        ["git", "branch", "--list"],
        cwd=str(repo_dir),
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "chore/bump-deps-nochange-repo" not in branches
