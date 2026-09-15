"""Focused safety checks for host resource sampling and cache cleanup."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]
CLEAR_CACHES = (
    ROOT / "universal_skills/system/host-disk-reclaimer/scripts/clear_caches.sh"
)
DISCOVER_DISK = (
    ROOT / "universal_skills/system/host-disk-reclaimer/scripts/discover_disk.sh"
)
CONSOLIDATE_VENVS = (
    ROOT / "universal_skills/system/host-disk-reclaimer/scripts/consolidate_venvs.sh"
)
SAMPLE_RESOURCES = (
    ROOT / "universal_skills/system/host-resource-sampler/scripts/sample_resources.py"
)


def isolated_env(home: Path) -> dict[str, str]:
    return os.environ | {
        "HOME": str(home),
        "PIP_CACHE_DIR": str(home / ".cache/pip"),
        "PRE_COMMIT_HOME": str(home / ".cache/pre-commit"),
        "UV_CACHE_DIR": str(home / ".cache/uv"),
        "XDG_CACHE_HOME": str(home / ".cache"),
    }


def test_clear_caches_defaults_to_a_real_dry_run(tmp_path: Path) -> None:
    home = tmp_path / "home"
    repo = tmp_path / "repo"
    package_cache = home / ".cache/torch/keep.bin"
    tool_cache = repo / "pkg/__pycache__/keep.pyc"
    package_cache.parent.mkdir(parents=True)
    tool_cache.parent.mkdir(parents=True)
    package_cache.write_bytes(b"keep")
    tool_cache.write_bytes(b"keep")

    completed = subprocess.run(
        [str(CLEAR_CACHES), str(repo)],
        env=isolated_env(home),
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Dry-run only; nothing was deleted." in completed.stdout
    assert package_cache.read_bytes() == b"keep"
    assert tool_cache.read_bytes() == b"keep"


def test_clear_caches_refuses_a_broad_root(tmp_path: Path) -> None:
    completed = subprocess.run(
        [str(CLEAR_CACHES), "/"],
        env=isolated_env(tmp_path / "home"),
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "refusing unsafe broad REPO_ROOT" in completed.stderr


def test_clear_caches_requires_apply_before_removing_candidates(tmp_path: Path) -> None:
    home = tmp_path / "home"
    repo = tmp_path / "repo"
    package_cache = home / ".cache/torch/remove.bin"
    tool_cache = repo / "pkg/.pytest_cache/remove.bin"
    package_cache.parent.mkdir(parents=True)
    tool_cache.parent.mkdir(parents=True)
    package_cache.write_bytes(b"remove")
    tool_cache.write_bytes(b"remove")

    completed = subprocess.run(
        [str(CLEAR_CACHES), "--apply", str(repo)],
        env=isolated_env(home),
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Applied cache cleanup." in completed.stdout
    assert not package_cache.exists()
    assert not tool_cache.exists()


def test_disk_discovery_reports_byte_and_inode_thresholds(tmp_path: Path) -> None:
    home = tmp_path / "home"
    target = tmp_path / "target"
    target.mkdir()
    completed = subprocess.run(
        [str(DISCOVER_DISK), str(target)],
        env=isolated_env(home)
        | {
            "DISK_BYTE_WARN_PCT": "0",
            "DISK_INODE_WARN_PCT": "0",
            "DU_TIMEOUT_SECONDS": "1",
        },
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Filesystem bytes (warning at 0%)" in completed.stdout
    assert "Filesystem inodes (warning at 0%)" in completed.stdout
    assert "WARN" in completed.stdout


def test_venv_consolidation_removes_only_a_verified_candidate(tmp_path: Path) -> None:
    shared = tmp_path / "shared"
    packages = tmp_path / "packages"
    shared_python = shared / "bin/python"
    old_venv_file = packages / "json/.venv/keep-before-apply"
    shared_python.parent.mkdir(parents=True)
    shared_python.symlink_to(sys.executable)
    old_venv_file.parent.mkdir(parents=True)
    (packages / "json/pyproject.toml").write_text("[project]\nname='json'\n")
    old_venv_file.write_text("candidate")

    dry_run = subprocess.run(
        [str(CONSOLIDATE_VENVS), str(shared), str(packages)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Dry-run only" in dry_run.stdout
    assert old_venv_file.exists()

    applied = subprocess.run(
        [str(CONSOLIDATE_VENVS), str(shared), str(packages), "--apply"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "removed 1 verified redundant venv" in applied.stdout
    assert not old_venv_file.exists()


def test_resource_sample_includes_pressure_cgroup_and_inode_data(
    tmp_path: Path,
) -> None:
    measured = tmp_path / "measured"
    measured.mkdir()
    completed = subprocess.run(
        [
            str(SAMPLE_RESOURCES),
            "--size-path",
            str(measured),
            "--size-timeout",
            "2",
        ],
        env=isolated_env(tmp_path / "home"),
        check=True,
        capture_output=True,
        text=True,
    )
    sample = json.loads(completed.stdout)

    assert sample["schema"] == "host-resource-sample/v1"
    assert set(sample["pressure"]) == {"cpu", "memory", "io"}
    assert "memory_events" in sample["cgroup_v2"]
    assert sample["filesystems"]
    assert all("inodes_used_pct" in item for item in sample["filesystems"])
    assert all("inode_warning" in item for item in sample["filesystems"])
    assert any(
        item["path"] == str(measured) and item["status"] == "ok"
        for item in sample["directory_sizes"]
    )
