"""Materialize and verify the exact pinned shared theme without overwrites."""

from contextlib import contextmanager
import hashlib
from importlib.util import cache_from_source
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from quality_templates import PIPELINES_REV

SOURCE = Path(__file__).resolve().parent / "templates" / "pipelines-theme"


def _inventory(root: Path) -> dict[str, Path]:
    """Reject links and non-files before reading or copying snapshot bytes."""
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"shared theme snapshot is not a regular directory: {root}")
    files = {}
    directories = set()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"shared theme path escapes its source: {relative}")
        if path.is_dir():
            directories.add(relative)
        elif path.is_file():
            files[relative] = path
        else:
            raise ValueError(f"shared theme non-regular file: {relative}")
    # pip normally byte-compiles installed .py resources. Such caches are not
    # authoritative input and are never staged, but every path above is still
    # checked before any cache can be ignored.
    cache_files = set()
    if "provenance.json" in files:
        manifest = json.loads(files["provenance.json"].read_text())
        for relative in manifest["files"]:
            if relative not in files or not relative.endswith(".py"):
                continue
            for optimization in ("", "1", "2"):
                cached = Path(cache_from_source(relative, optimization=optimization))
                if cached.as_posix() in files:
                    cache_files.add(cached.as_posix())
    cache_directories = {Path(relative).parent.as_posix() for relative in cache_files}
    files = {
        relative: path
        for relative, path in files.items()
        if relative not in cache_files
    }
    expected_directories = {
        parent.as_posix()
        for relative in files
        for parent in Path(relative).parents
        if parent != Path(".")
    }
    if directories - cache_directories != expected_directories:
        raise ValueError("shared theme inventory includes unexpected empty directories")
    return files


def verified_source() -> Path:
    """Verify the complete shipped inventory against the reviewed provenance."""
    files = _inventory(SOURCE)
    manifest = json.loads(files["provenance.json"].read_text())
    if manifest["revision"] != PIPELINES_REV:
        raise ValueError("shared theme revision disagrees with the pipeline contract")
    for relative in manifest["files"]:
        path = SOURCE / relative
        if not path.resolve().is_relative_to(SOURCE.resolve()):
            raise ValueError("shared theme provenance path escapes its source")
    if set(files) != {"provenance.json", *manifest["files"]}:
        raise ValueError("shared theme source inventory differs from provenance")
    for relative, expected in manifest["files"].items():
        if hashlib.sha256(files[relative].read_bytes()).hexdigest() != expected:
            raise ValueError(f"shared theme snapshot differs: {relative}")
    return SOURCE


def _sync(source: Path, root: Path, mode: str) -> None:
    subprocess.run(
        [
            sys.executable,
            str(source / "scripts/sync_mkdocs_theme.py"),
            mode,
            "--root",
            str(root),
            "--source-root",
            str(source),
            "--content-source",
            "docs",
        ],
        check=True,
        capture_output=True,
        text=True,
    )


@contextmanager
def staged_theme_files():
    """Yield only verified source/destination pairs for the caller's safe copy."""
    source = verified_source()
    manifest = json.loads((source / "provenance.json").read_text())
    with TemporaryDirectory(prefix="mcp-theme-") as temporary:
        stage = Path(temporary)
        _sync(source, stage, "sync")
        files = [(path, Path(relative)) for relative, path in _inventory(stage).items()]
        files.extend(
            (source / relative, Path(".pipeline-theme") / relative)
            for relative in sorted({"provenance.json", *manifest["files"]})
        )
        yield files


def validate_theme_destinations(root: Path, relatives) -> None:
    """Refuse redirected destinations before creating any copied theme file."""
    for relative in relatives:
        destination = root / relative
        if not destination.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"shared theme destination escapes project: {relative}")
        for component in (destination, *destination.parents):
            if component.is_symlink():
                raise ValueError(f"shared theme destination is a symlink: {relative}")
            if component == root:
                break


def check_shared_theme(root: Path) -> None:
    """Check inherited configuration and rendered assets against the authority."""
    source = verified_source()
    expected = _inventory(source)
    actual = _inventory(root / ".pipeline-theme")
    if actual.keys() != expected.keys():
        raise ValueError("shared theme destination inventory differs from provenance")
    for relative, original in expected.items():
        copied = actual[relative]
        if copied.read_bytes() != original.read_bytes():
            raise ValueError(f"shared theme destination differs: {relative}")
        if copied.stat().st_mode & 0o111 != original.stat().st_mode & 0o111:
            raise ValueError(
                f"shared theme destination executable mode differs: {relative}"
            )
    _sync(source, root, "check")
