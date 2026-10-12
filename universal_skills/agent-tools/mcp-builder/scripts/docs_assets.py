"""Materialize the exact pinned shared theme without overwriting project files."""

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from quality_templates import PIPELINES_REV

SOURCE = Path(__file__).resolve().parent / "templates" / "pipelines-theme"


def verified_source() -> Path:
    """Verify all shipped upstream files against the reviewed provenance."""
    manifest = json.loads((SOURCE / "provenance.json").read_text())
    if manifest["revision"] != PIPELINES_REV:
        raise ValueError("shared theme revision disagrees with the pipeline contract")
    for relative, expected in manifest["files"].items():
        path = SOURCE / relative
        if not path.resolve().is_relative_to(SOURCE.resolve()) or path.is_symlink():
            raise ValueError("shared theme provenance path escapes its source")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
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
    """Yield authoritative source/destination pairs for the caller's safe copy."""
    source = verified_source()
    with TemporaryDirectory(prefix="mcp-theme-") as temporary:
        stage = Path(temporary)
        _sync(source, stage, "sync")
        files = [
            (path, path.relative_to(stage))
            for path in sorted(stage.rglob("*"))
            if path.is_file()
        ]
        files.extend(
            (path, Path(".pipeline-theme") / path.relative_to(source))
            for path in sorted(source.rglob("*"))
            if path.is_file() and "__pycache__" not in path.parts
        )
        yield files


def check_shared_theme(root: Path) -> None:
    """Keep the authority's strict byte comparison on the materialized project."""
    _sync(verified_source(), root, "check")
