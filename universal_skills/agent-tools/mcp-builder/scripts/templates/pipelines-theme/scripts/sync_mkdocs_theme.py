"""Synchronize generated ecosystem MkDocs theme files into a consumer repo."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class ThemeFile:
    """A canonical source file and its generated consumer-relative path."""

    source: str
    destination: str
    content_relative: bool = True


THEME_FILES = (
    ThemeFile("extra.css", "stylesheets/extra.css"),
    ThemeFile("assets/graph-mark.svg", "assets/graph-mark.svg"),
    ThemeFile("assets/favicon.svg", "assets/favicon.svg"),
    ThemeFile("assets/runtime-architecture.mmd", "assets/runtime-architecture.mmd"),
    ThemeFile("assets/runtime-architecture.svg", "assets/runtime-architecture.svg"),
    ThemeFile(
        "assets/brands/epistemic-graph-logo-v1.png",
        "assets/brands/epistemic-graph-logo-v1.png",
    ),
    ThemeFile(
        "assets/brands/agent-utilities-logo-v1.png",
        "assets/brands/agent-utilities-logo-v1.png",
    ),
    ThemeFile("assets/brands/graph-os-logo-v1.png", "assets/brands/graph-os-logo-v1.png"),
    ThemeFile(
        "assets/brands/agent-connector-sdk-logo-v1.png",
        "assets/brands/agent-connector-sdk-logo-v1.png",
    ),
    ThemeFile(
        "assets/brands/agent-webui-logo-v1.png",
        "assets/brands/agent-webui-logo-v1.png",
    ),
    ThemeFile("assets/brands/geniusbot-logo-v1.png", "assets/brands/geniusbot-logo-v1.png"),
    ThemeFile(
        "assets/brands/agent-terminal-ui-logo-v1.png",
        "assets/brands/agent-terminal-ui-logo-v1.png",
    ),
    ThemeFile("glossary.md", "glossary.md"),
)


RUNTIME_PROVENANCE = re.compile(
    rb"<!-- Generated compatibility copy; do not edit\.\n"
    rb"Source: https://raw\.githubusercontent\.com/Knuckles-Team/epistemic-graph/"
    rb"[0-9a-f]{40}/docs/assets/runtime-architecture\.svg\n"
    rb"SHA-256: (?P<digest>[0-9a-f]{64})\n"
    rb"Synchronize: https://github\.com/Knuckles-Team/\.github/blob/main/docs/runtime-diagram\.md\n"
    rb"-->\n(?P<payload>.*)",
    re.DOTALL,
)


class ThemeSyncError(Exception):
    """The source, destination, or content-source contract is invalid."""


def _safe_relative_path(value: str, label: str) -> Path:
    path = Path(value)
    if path.is_absolute() or not path.parts or any(part in {".", ".."} for part in path.parts):
        raise ThemeSyncError(f"{label} must be a contained relative path")
    return path


def _contained(root: Path, relative: Path, label: str) -> Path:
    base = root.resolve()
    result = (base / relative).resolve()
    if not result.is_relative_to(base):
        raise ThemeSyncError(f"{label} escapes the repository root")
    return result


def _check_file(destination: Path, expected: bytes, repository: Path) -> str | None:
    """Describe how ``destination`` diverges from ``expected``, or ``None`` when it matches."""
    try:
        actual = destination.read_bytes()
    except OSError:
        return f"missing generated file: {destination.relative_to(repository)}"
    if actual != expected:
        return f"generated file differs: {destination.relative_to(repository)}"
    return None


def _runtime_diagram_content(destination: Path, expected: bytes) -> bytes:
    """Keep the canonical sync tool's provenance without accepting SVG drift."""
    if not destination.is_file():
        return expected
    actual = destination.read_bytes()
    if not actual.startswith(b"<!--"):
        return expected
    provenance = RUNTIME_PROVENANCE.fullmatch(actual)
    if (
        provenance is None
        or provenance["digest"] != hashlib.sha256(expected).hexdigest().encode()
        or provenance["payload"] != expected
    ):
        raise ThemeSyncError(
            "runtime diagram provenance or payload differs; use the canonical "
            "sync guide: https://github.com/Knuckles-Team/.github/blob/main/docs/runtime-diagram.md"
        )
    return actual


def _expected_content(item: ThemeFile, source_file: Path, destination: Path) -> bytes:
    """Resolve exact theme bytes while preserving validated runtime provenance."""
    expected = source_file.read_bytes()
    if item.source == "assets/runtime-architecture.svg":
        return _runtime_diagram_content(destination, expected)
    return expected


def sync_theme(
    *,
    source_root: Path,
    repository_root: Path,
    content_source: str,
    mode: Literal["sync", "check"],
) -> list[str]:
    """Copy canonical files in ``sync`` mode or return mismatches in ``check`` mode."""
    content_relative = _safe_relative_path(content_source, "content-source")
    repository = repository_root.resolve()
    content_root = _contained(repository, content_relative, "content-source")
    source = (source_root / "templates" / "mkdocs-theme").resolve()
    if not source.is_dir():
        raise ThemeSyncError(f"canonical theme directory does not exist: {source}")

    mismatches: list[str] = []
    for item in THEME_FILES:
        source_file = source / item.source
        if not source_file.is_file():
            raise ThemeSyncError(f"canonical theme file does not exist: {source_file}")
        destination_root = content_root if item.content_relative else repository
        destination = _contained(destination_root, Path(item.destination), item.destination)
        expected = _expected_content(item, source_file, destination)
        if mode == "check":
            mismatch = _check_file(destination, expected, repository)
            if mismatch:
                mismatches.append(mismatch)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(expected)

    return mismatches


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("sync", "check"))
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="consumer repository root")
    parser.add_argument(
        "--content-source",
        default="docs",
        help="consumer MkDocs content directory (normally docs or pages)",
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="pipelines checkout containing templates/mkdocs-theme",
    )
    args = parser.parse_args(argv)
    try:
        mismatches = sync_theme(
            source_root=args.source_root,
            repository_root=args.root,
            content_source=args.content_source,
            mode=args.mode,
        )
    except (OSError, ThemeSyncError) as exc:
        print(f"shared MkDocs theme: CANNOT RUN: {exc}", file=sys.stderr)
        return 2
    if mismatches:
        print("shared MkDocs theme: generated files are out of sync:", file=sys.stderr)
        for mismatch in mismatches:
            print(f"  - {mismatch}", file=sys.stderr)
        return 1
    print(f"shared MkDocs theme: {args.mode} complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
