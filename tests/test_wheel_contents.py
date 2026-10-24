"""Distribution-level checks for the skill catalog wheel."""

from __future__ import annotations

import importlib.util
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
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
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
    if relative_path.parts[:3] == ("skills", "comparative-analysis", "results"):
        return True
    return (
        relative_path.parts[:2] == ("skills", "comparative-analysis")
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
        "skills/mcp-builder/build/nested/wheel_leak.py": "BUILD_JUNK = True\n",
        "skills/mcp-builder/dist/nested/wheel_leak.py": "DIST_JUNK = True\n",
        "skills/mcp-builder/generated.egg-info/nested/wheel_leak.py": "EGG_INFO_JUNK = True\n",
    }
    for relative_path, contents in generated_package_junk.items():
        junk = project / "universal_skills" / relative_path
        junk.parent.mkdir(parents=True, exist_ok=True)
        junk.write_text(contents, encoding="utf-8")

    near_miss_resources = {
        "skills/mcp-builder/build-tools/readiness_fixture.md": "BUILD_TOOL_RESOURCE\n",
        "skills/mcp-builder/dist-tools/readiness_fixture.md": "DIST_TOOL_RESOURCE\n",
        "skills/mcp-builder/egg-info-tools/readiness_fixture.md": "EGG_INFO_TOOL_RESOURCE\n",
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
        "universal_skills/skills/mcp-builder/SKILL.md",
        "universal_skills/skills/mcp-builder/scripts/scaffold_connector.py",
        "universal_skills/skills/mcp-builder/scripts/github_publish.py",
        "universal_skills/skills/mcp-builder/scripts/github_pages.py",
        "universal_skills/skills/mcp-builder/scripts/agent_readiness.py",
        "universal_skills/skills/mcp-builder/scripts/agent_readiness_schema.json",
    }
    assert readiness_resources <= members
    assert (
        "universal_skills/skills/mcp-builder/scripts/github_template.py"
        not in members
    )
    assert not any(
        member.startswith(
            (
                "universal_skills/agent-tools/agent-builder/",
                "universal_skills/agent-tools/agent-package-builder/",
                "universal_skills/agent-tools/api-client-builder/",
            )
        )
        for member in members
    )

    # Exercise normal pip byte-compilation, not just ZIP extraction. The target
    # is isolated and no dependencies or host environment are installed/changed.
    installed = tmp_path / "installed"
    pip = shutil.which("pip") or shutil.which("pip3")
    assert pip, "the wheel install acceptance check requires an existing pip"
    installation = subprocess.run(
        [
            pip,
            "--python",
            sys.executable,
            "install",
            "--no-deps",
            "--no-index",
            "--disable-pip-version-check",
            "--target",
            str(installed),
            str(wheel),
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert installation.returncode == 0, installation.stdout + installation.stderr
    installed_scripts = installed / "universal_skills/skills/mcp-builder/scripts"
    generated = tmp_path / "generated"
    scaffold = subprocess.run(
        [
            sys.executable,
            str(installed_scripts / "scaffold_connector.py"),
            "installed-wheel",
            "--output-dir",
            str(generated),
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert scaffold.returncode == 0, scaffold.stdout + scaffold.stderr
    assert (generated / "installed-wheel/pyproject.toml").is_file()
    assert (generated / "installed-wheel/installed_wheel/connector_sources.py").is_file()
    resource_check = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            (
                "import importlib, importlib.resources, json, sys; "
                "sys.path.insert(0, sys.argv[1]); "
                "package = 'universal_skills.skills.mcp-builder.scripts'; "
                "module = importlib.import_module(package + '.agent_readiness'); "
                "assert callable(module.main); "
                "schema = json.loads(importlib.resources.files(package)"
                ".joinpath('agent_readiness_schema.json').read_text()); "
                "assert schema['$schema']"
            ),
            str(installed),
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert resource_check.returncode == 0, resource_check.stdout + resource_check.stderr
    assert {f"universal_skills/{path}" for path in near_miss_resources} <= members

    packaged_junk = sorted(
        member
        for member in members
        if member.startswith("universal_skills/")
        and _is_generated_or_cache(
            PurePosixPath(member).relative_to("universal_skills")
        )
    )
    assert not packaged_junk, (
        f"wheel contains generated/cache files: {packaged_junk[:20]}"
    )
    assert not any(
        member.startswith(("build/", "scripts/", "tests/")) for member in members
    )
