"""Distribution-level checks for the skill catalog wheel."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path, PurePosixPath

from setuptools import find_namespace_packages


ROOT = Path(__file__).resolve().parents[1]
CACHE_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
}
GENERATED_PACKAGE_DIRS = {"build", "dist", "egg-info"}


def test_namespace_discovery_excludes_generated_directories(tmp_path: Path) -> None:
    """Generated namespace trees must not become distributable packages."""
    config = tomllib.loads(
        (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    package_find = config["tool"]["setuptools"]["packages"]["find"]
    project = tmp_path / "project"
    for relative_path in (
        "universal_skills/build/generated",
        "universal_skills/dist/generated",
        "universal_skills/egg-info/generated",
        "universal_skills/legitimate/domain",
    ):
        (project / relative_path).mkdir(parents=True)

    packages = set(
        find_namespace_packages(
            where=str(project),
            include=package_find["include"],
            exclude=package_find["exclude"],
        )
    )

    assert "universal_skills.legitimate" in packages
    assert "universal_skills.legitimate.domain" in packages
    assert not any(
        part in {"build", "dist", "egg-info"}
        for package in packages
        for part in package.split(".")
    )


def _is_generated_or_cache(relative_path: PurePosixPath) -> bool:
    if CACHE_DIRS.intersection(relative_path.parts):
        return True
    if GENERATED_PACKAGE_DIRS.intersection(relative_path.parts):
        return True
    if any(part.endswith(".egg-info") for part in relative_path.parts):
        return True
    if relative_path.suffix in {".pyc", ".pyo", ".skill"}:
        return True
    if relative_path.parts[:3] == ("research", "comparative-analysis", "results"):
        return True
    return (
        relative_path.parts[:2] == ("research", "comparative-analysis")
        and relative_path.name.startswith("results_")
        and relative_path.suffix == ".json"
    )


def test_wheel_contains_catalog_resources_without_build_junk(tmp_path: Path) -> None:
    """A clean wheel carries authored skill files, including hidden template assets."""
    project = tmp_path / "project"
    project.mkdir()
    for filename in ("pyproject.toml", "README.md", "LICENSE"):
        shutil.copy2(ROOT / filename, project / filename)
    shutil.copytree(
        ROOT / "universal_skills",
        project / "universal_skills",
        ignore=shutil.ignore_patterns(
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "*.pyc",
            "*.pyo",
        ),
    )

    # Namespace discovery used to leak these project-level directories into the wheel.
    for directory in ("build/lib", "scripts", "tests"):
        leak = project / directory / "wheel_leak.py"
        leak.parent.mkdir(parents=True, exist_ok=True)
        leak.write_text("SHOULD_NOT_BE_PACKAGED = True\n", encoding="utf-8")

    generated_package_junk = {
        "build/nested/wheel_leak.py": "BUILD_JUNK = True\n",
        "dist/nested/wheel_leak.py": "DIST_JUNK = True\n",
        "egg-info/nested/wheel_leak.py": "EGG_INFO_JUNK = True\n",
        "agent-tools/agent-builder/build/nested/wheel_leak.py": "BUILD_JUNK = True\n",
        "agent-tools/agent-builder/dist/nested/wheel_leak.py": "DIST_JUNK = True\n",
        "agent-tools/agent-builder/generated.egg-info/nested/wheel_leak.py": "EGG_INFO_JUNK = True\n",
    }
    for relative_path, contents in generated_package_junk.items():
        junk = project / "universal_skills" / relative_path
        junk.parent.mkdir(parents=True, exist_ok=True)
        junk.write_text(contents, encoding="utf-8")

    near_miss_resources = {
        "agent-tools/agent-builder/build-tools/readiness_fixture.md": "BUILD_TOOL_RESOURCE\n",
        "agent-tools/agent-builder/dist-tools/readiness_fixture.md": "DIST_TOOL_RESOURCE\n",
        "agent-tools/agent-builder/egg-info-tools/readiness_fixture.md": "EGG_INFO_TOOL_RESOURCE\n",
    }
    for relative_path, contents in near_miss_resources.items():
        resource = project / "universal_skills" / relative_path
        resource.parent.mkdir(parents=True, exist_ok=True)
        resource.write_text(contents, encoding="utf-8")

    # Exercise cache exclusions even when the source checkout itself is pristine.
    catalog_junk = {
        "core/__pycache__/wheel_leak.pyc": b"not bytecode",
        "core/.ruff_cache/wheel_leak": b"not a cache",
        "core/generated.skill": b"not a source asset",
    }
    for relative_path, contents in catalog_junk.items():
        junk = project / "universal_skills" / relative_path
        junk.parent.mkdir(parents=True, exist_ok=True)
        junk.write_bytes(contents)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(project / "dist"),
        ],
        cwd=project,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr

    wheel = next((project / "dist").glob("*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        members = set(archive.namelist())

    source_root = project / "universal_skills"
    expected = {
        f"universal_skills/{path.relative_to(source_root).as_posix()}"
        for path in source_root.rglob("*")
        if path.is_file()
        and not _is_generated_or_cache(
            PurePosixPath(path.relative_to(source_root).as_posix())
        )
    }
    missing = sorted(expected - members)
    assert not missing, f"wheel omitted catalog resources: {missing[:20]}"

    readiness_resources = {
        "universal_skills/agent-tools/agent-builder/SKILL.md",
        "universal_skills/agent-tools/agent-package-builder/scripts/agent_readiness.py",
        "universal_skills/agent-tools/agent-package-builder/scripts/agent_readiness_schema.json",
    }
    assert readiness_resources <= members
    assert {
        f"universal_skills/{path}" for path in near_miss_resources
    } <= members

    packaged_junk = sorted(
        member
        for member in members
        if member.startswith("universal_skills/")
        and _is_generated_or_cache(
            PurePosixPath(member).relative_to("universal_skills")
        )
    )
    assert not packaged_junk, f"wheel contains generated/cache files: {packaged_junk[:20]}"
    assert not any(
        member.startswith(("build/", "scripts/", "tests/")) for member in members
    )
