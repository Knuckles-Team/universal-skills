#!/usr/bin/env python3
"""Run the generated package's fail-closed structural quality gates.

The package builder emits this small dispatcher instead of relying on a
network-backed pre-commit environment.  The host or CI image provisions the
native tools; this module only resolves an already-installed binary, verifies
the pinned version, selects the staged/delta universe, and validates output.

Modes:

``cccc``
    Measure changed source files at the 10/15 cyclomatic/cognitive caps.
``cccc-census``
    Measure every tracked source file at the 10/15 caps.
``dupehound``
    Ask dupehound for new whole-function twins in the changed source surface.
``kiss-census``
    Run the full-tree KISS census through the generated shell wrapper.
``jscpd``
    Compare a full all-format candidate tree with its base tree.  Python is
    intentionally included so copied blocks inside distinct functions are
    caught in addition to dupehound's structural function check.  A real
    pre-push uses pre-commit's PRE_COMMIT_FROM_REF/TO_REF range; manual runs
    default to main...HEAD.
``jscpd-census``
    Report the full current-tree clone count.  Findings are advisory, but a
    missing, drifted, or malformed scanner is still an error.
``import-linter``
    Run the checked-in package architecture contracts when Python changed.

Exit status 0 means the applicable check ran and passed, 1 means a real
quality finding, and 2 means the check could not be trusted.  No mode installs
packages, edits source, creates baselines, or writes reports inside the repo.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import Any, NoReturn


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
CCCC_CONFIG = ROOT / ".cccc.toml"
KISS_CONFIG = ROOT / ".kiss" / "kiss.toml"
IMPORTLINTER_CONFIG = ROOT / ".importlinter"

SUPPORTED_SOURCE_SUFFIXES = frozenset(
    {
        ".c",
        ".c++",
        ".cc",
        ".cjs",
        ".cpp",
        ".cts",
        ".cs",
        ".cxx",
        ".go",
        ".h",
        ".hh",
        ".h++",
        ".hpp",
        ".hxx",
        ".java",
        ".js",
        ".jsx",
        ".kt",
        ".mjs",
        ".mts",
        ".php",
        ".py",
        ".pyi",
        ".rb",
        ".rs",
        ".scala",
        ".swift",
        ".ts",
        ".tsx",
    }
)

# jscpd is intentionally broad.  These are directory/file classes that are
# generated, third-party, or fixture data rather than maintainable product
# source.  Python is absent from this list by design.
EXCLUDED_DIRECTORY_NAMES = frozenset(
    {
        ".git",
        ".venv",
        ".venv-base",
        "venv",
        "env",
        "node_modules",
        ".cache",
        "target",
        "target-isolated",
        "dist",
        "dist-primary",
        "dist-reproduction",
        "build",
        "build-artifacts",
        "coverage",
        "htmlcov",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".pytest_tmp",
        ".ruff_cache",
        ".hypothesis",
        ".tox",
        ".eggs",
        "site-packages",
        "vendor",
        "third_party",
        "generated",
        "codegen",
        "fixtures",
        "fixture",
        "samples",
        "sample",
        "examples",
        "__snapshots__",
        "__generated__",
        "openapi_client",
        "graphql_client",
    }
)
EXCLUDED_FILE_NAMES = frozenset(
    {
        ".env",
        ".env.local",
        ".jscpd.json",
        ".jscpdrc",
        "jscpd.config.js",
        "jscpd.config.cjs",
    }
)
EXCLUDED_GLOBS = (
    "**/*.lock",
    "**/*.lock.*",
    "**/.git/**",
    "**/.venv/**",
    "**/.venv-base/**",
    "**/venv/**",
    "**/env/**",
    "**/node_modules/**",
    "**/.cache/**",
    "**/target/**",
    "**/target-isolated/**",
    "**/dist/**",
    "**/dist-primary/**",
    "**/dist-reproduction/**",
    "**/build/**",
    "**/build-artifacts/**",
    "**/coverage/**",
    "**/htmlcov/**",
    "**/__pycache__/**",
    "**/.mypy_cache/**",
    "**/.pytest_cache/**",
    "**/.pytest_tmp/**",
    "**/.ruff_cache/**",
    "**/.hypothesis/**",
    "**/.tox/**",
    "**/.eggs/**",
    "**/site-packages/**",
    "**/*.egg-info/**",
    "**/vendor/**",
    "**/third_party/**",
    "**/generated/**",
    "**/codegen/**",
    "**/fixtures/**",
    "**/fixture/**",
    "**/samples/**",
    "**/sample/**",
    "**/examples/**",
    "**/__snapshots__/**",
    "**/__generated__/**",
    "**/openapi_client/**",
    "**/graphql_client/**",
    "**/*.generated.*",
    "**/*.map",
    "**/*.min.css",
    "**/*.min.js",
    "**/*lock",
    "**/*lock.*",
)

# jscpd discovers these from its process working directory without requiring a
# --config flag. A repository-local config could therefore silently override a
# command-line option that this wrapper did not remember to pin. Refuse all
# known names instead of trusting a report produced under ambient policy.
JSCPD_CONFIG_NAMES = frozenset(
    {
        ".jscpd.json",
        ".jscpdrc",
        ".jscpdrc.json",
        ".jscpdrc.yaml",
        ".jscpdrc.yml",
        "jscpd.config.js",
        "jscpd.config.cjs",
    }
)

# Release tools do not agree on whether a patch component is printed: for
# example, import-linter publishes ``2.14`` while the Rust tools use three
# components.  Accept only exact two- or three-component numeric releases.
_VERSION_RE = re.compile(r"(?<!\d)(\d+\.\d+(?:\.\d+)?)(?!\d)")
_VERSION_OUTPUT_LABELS = {
    "cccc": "cccc",
    "kiss": "kiss",
    "dupehound": "dupehound",
    # jscpd v5 deliberately reports itself as cpd.
    "jscpd": "cpd",
    "import-linter": "import-linter",
}


class ScannerError(RuntimeError):
    """An unavailable, drifted, or malformed scanner contract."""


def _fail(message: str) -> NoReturn:
    raise ScannerError(message)


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            document = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        _fail(f"cannot read {path}: {exc}")
    if not isinstance(document, dict):
        _fail(f"{path} did not contain a TOML table")
    return document


def _scanner_config() -> dict[str, Any]:
    document = _read_toml(PYPROJECT)
    try:
        table = document["tool"]["agent_utilities"]["scanners"]
    except (KeyError, TypeError):
        _fail(
            "pyproject.toml has no [tool.agent_utilities.scanners] table; "
            "refusing unpinned scanner defaults"
        )
    if not isinstance(table, dict):
        _fail("[tool.agent_utilities.scanners] must be a TOML table")
    required = (
        "cccc_version",
        "kiss_version",
        "dupehound_version",
        "jscpd_version",
        "import_linter_version",
        "cccc_max_cyclomatic",
        "cccc_max_cognitive",
        "dupehound_threshold",
        "dupehound_min_tokens",
        "jscpd_min_tokens",
        "jscpd_min_lines",
        "jscpd_mode",
    )
    missing = [key for key in required if key not in table]
    if missing:
        _fail(f"scanner profile is missing {', '.join(missing)}")
    for key in (
        "cccc_version",
        "kiss_version",
        "dupehound_version",
        "jscpd_version",
        "import_linter_version",
    ):
        value = table[key]
        if not isinstance(value, str) or not _VERSION_RE.fullmatch(value):
            _fail(f"{key} must be an exact numeric release version")
    if table["jscpd_mode"] not in {"mild", "weak", "strict"}:
        _fail("jscpd_mode must be mild, weak, or strict")
    for key in (
        "cccc_max_cyclomatic",
        "cccc_max_cognitive",
        "dupehound_min_tokens",
        "jscpd_min_tokens",
        "jscpd_min_lines",
    ):
        value = table[key]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            _fail(f"{key} must be a positive integer")
    threshold = table["dupehound_threshold"]
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        _fail("dupehound_threshold must be a number")
    if not 0.0 <= float(threshold) <= 1.0:
        _fail("dupehound_threshold must be between 0 and 1")
    return table


def _tool(name: str, environment_name: str, config: dict[str, Any]) -> str:
    configured = os.environ.get(environment_name)
    if configured:
        candidate = Path(configured).expanduser()
        if not candidate.is_absolute():
            candidate = ROOT / candidate
        if not candidate.is_file() or not os.access(candidate, os.X_OK):
            _fail(
                f"{environment_name} points to a missing or non-executable "
                f"scanner: {configured!r}"
            )
        return str(candidate)
    candidates = [
        ROOT / ".tools" / name,
        Path.home() / ".local" / "bin" / name,
        Path("/usr/local/bin") / name,
    ]
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    found = shutil.which(name)
    if found:
        return found
    _fail(
        f"{name} is not installed. Set {environment_name} or provision the "
        "reviewed toolchain; hooks never install scanners"
    )


def _verify_version(executable: str, expected: str, name: str) -> None:
    try:
        result = subprocess.run(
            [executable, "--version"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        _fail(f"could not run {name} --version: {exc}")
    if result.returncode != 0:
        _fail(f"{name} --version exited {result.returncode}")
    actual = (result.stdout or "").strip()
    label = _VERSION_OUTPUT_LABELS.get(name)
    expected_output = f"{label} {expected}" if label else None
    if expected_output is not None and actual != expected_output:
        _fail(
            f"{name} version identity drift: want {expected_output!r}, got "
            f"{actual[:200]!r}"
        )
    if expected_output is None:
        versions = _VERSION_RE.findall(f"{result.stdout}\n{result.stderr}")
        if versions != [expected]:
            _fail(
                f"{name} version drift: want {expected}, got "
                f"{(result.stdout or result.stderr).strip()[:200]!r}"
            )


def _git(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, UnicodeError) as exc:
        _fail(f"could not execute git: {exc}")
    if result.returncode != 0:
        _fail(f"git {' '.join(args)} failed: {(result.stderr or '').strip()[:400]}")
    return result.stdout


def _normalise(path: str) -> str:
    normalised = PurePosixPath(path.replace("\\", "/")).as_posix()
    while normalised.startswith("./"):
        normalised = normalised[2:]
    if normalised == ".." or normalised.startswith("../"):
        _fail(f"git returned an unsafe path: {path!r}")
    return normalised


def changed_paths(base_ref: str | None = None, target_ref: str = "HEAD") -> list[str]:
    """Return staged paths or a commit-range path set, never all repo files."""

    if base_ref:
        output = _git(
            "diff",
            "--name-only",
            "--diff-filter=ACMRD",
            f"{base_ref}...{target_ref}",
        )
    else:
        output = _git("diff", "--cached", "--name-only", "--diff-filter=ACMRD")
        if not output.strip():
            output = _git("diff", "--name-only", "--diff-filter=ACMRD", "HEAD")
            output += _git("ls-files", "--others", "--exclude-standard")
    return sorted({_normalise(path) for path in output.splitlines() if path.strip()})


def _excluded(path: str) -> bool:
    candidate = PurePosixPath(path)
    if candidate.name in EXCLUDED_FILE_NAMES:
        return True
    if any(part in EXCLUDED_DIRECTORY_NAMES for part in candidate.parts):
        return True
    return any(fnmatch.fnmatch(path, pattern) for pattern in EXCLUDED_GLOBS)


def _source_paths(paths: list[str]) -> list[str]:
    return sorted(
        {
            path
            for path in paths
            if PurePosixPath(path).suffix.lower() in SUPPORTED_SOURCE_SUFFIXES
            and not _excluded(path)
        }
    )


def _python_paths(paths: list[str]) -> list[str]:
    return sorted(
        {
            path
            for path in paths
            if PurePosixPath(path).suffix.lower() in {".py", ".pyi"}
            and not _excluded(path)
        }
    )


def _jscpd_paths(paths: list[str]) -> list[str]:
    # Do not narrow this to dupehound's language list: jscpd is the wide-net
    # detector for Python blocks, templates, SQL, YAML, CSS, and configuration.
    return sorted({path for path in paths if not _excluded(path)})


def _tracked_paths() -> list[str]:
    """Return tracked plus standard untracked paths for a full-tree census."""

    return sorted(
        {
            _normalise(path)
            for output in (
                _git("ls-files"),
                _git("ls-files", "--others", "--exclude-standard"),
            )
            for path in output.splitlines()
            if path.strip()
        }
    )


def _all_source_paths() -> list[str]:
    return _source_paths(_tracked_paths())


def _staged_blob(path: str) -> bytes | None:
    try:
        result = subprocess.run(
            ["git", "show", f":{path}"],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        _fail(f"could not read staged blob {path}: {exc}")
    if result.returncode == 0:
        return result.stdout
    candidate = ROOT / path
    if not candidate.is_file():
        # A deleted path is a valid change, but it has no post-change source
        # blob to score. The architecture gate still sees it through the
        # deleted path returned by changed_paths().
        return None
    try:
        return candidate.read_bytes()
    except OSError as exc:
        _fail(f"cannot read changed source {path}: {exc}")


def _materialise_staged(path: str, parent: Path) -> Path | None:
    target = parent / path
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        blob = _staged_blob(path)
        if blob is None:
            return None
        target.write_bytes(blob)
    except OSError as exc:
        _fail(f"cannot materialise staged source {path}: {exc}")
    return target


def _reference_blob(ref: str, path: str) -> bytes | None:
    """Read a file from a ref, distinguishing absence from Git failure."""

    try:
        exists = subprocess.run(
            ["git", "cat-file", "-e", f"{ref}:{path}"],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        _fail(f"could not inspect {ref}:{path}: {exc}")
    if exists.returncode == 1:
        return None
    if exists.returncode != 0:
        # `git cat-file -e ref:path` returns 128 for a valid ref with a
        # missing path (not 1). Confirm the ref/path distinction with
        # ls-tree; a failing ls-tree remains a real Git error.
        missing = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", ref, "--", path],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
        if missing.returncode == 0 and not missing.stdout.strip():
            return None
        detail = missing.stderr or exists.stderr or b""
        _fail(
            f"could not inspect {ref}:{path}: "
            f"{detail.decode(errors='replace').strip()[:300]}"
        )
    try:
        result = subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        _fail(f"could not read {ref}:{path}: {exc}")
    if result.returncode != 0:
        _fail(
            f"could not read {ref}:{path}: "
            f"{(result.stderr or b'').decode(errors='replace').strip()[:300]}"
        )
    return result.stdout


def _materialise_blob(blob: bytes, path: str, parent: Path) -> Path:
    target = parent / path
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        target.write_bytes(blob)
    except OSError as exc:
        _fail(f"cannot materialise source {path}: {exc}")
    return target


def _cccc_rows(
    executable: str, source: Path, relative: str
) -> dict[str, list[tuple[int, int, int]]]:
    """Return every nested CCCC function row, preserving duplicate names."""

    try:
        result = subprocess.run(
            [
                executable,
                "--config",
                str(CCCC_CONFIG),
                str(source),
                "--min",
                "0",
            ],
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        _fail(f"cccc could not scan {relative}: {exc}")
    if result.returncode > 1 or not result.stdout.strip():
        _fail(f"cccc failed for {relative}: {(result.stderr or '').strip()[:300]}")
    try:
        document = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        _fail(f"cccc returned invalid JSON for {relative}: {exc}")
    if not isinstance(document, dict) or not isinstance(document.get("files"), list):
        _fail(f"cccc returned no files array for {relative}")

    rows: dict[str, list[tuple[int, int, int]]] = {}

    def walk(function: object, prefix: str = "") -> None:
        if not isinstance(function, dict):
            _fail(f"cccc returned a malformed function row for {relative}")
        name = function.get("name")
        cyclomatic = function.get("cyclomatic")
        cognitive = function.get("cognitive")
        line = function.get("line", 0)
        if (
            not isinstance(name, str)
            or isinstance(cyclomatic, bool)
            or not isinstance(cyclomatic, int)
            or isinstance(cognitive, bool)
            or not isinstance(cognitive, int)
            or isinstance(line, bool)
            or not isinstance(line, int)
        ):
            _fail(f"cccc returned an incomplete row for {relative}")
        qualified = f"{prefix}{name}"
        rows.setdefault(qualified, []).append((cyclomatic, cognitive, line))
        children = function.get("children", [])
        if not isinstance(children, list):
            _fail(f"cccc returned malformed children for {relative}:{line}")
        for child in children:
            walk(child, f"{qualified}.")

    for report in document["files"]:
        if not isinstance(report, dict):
            _fail(f"cccc returned a malformed file row for {relative}")
        parse_errors = report.get("parse_errors", [])
        if not isinstance(parse_errors, list):
            _fail(f"cccc returned malformed parse errors for {relative}")
        if any(
            not isinstance(error, str) or not error.strip() for error in parse_errors
        ):
            _fail(f"cccc returned malformed parse errors for {relative}")
        if parse_errors:
            _fail(f"cccc could not parse {relative}: {parse_errors[0]!r}")
        functions = report.get("functions", [])
        if not isinstance(functions, list):
            _fail(f"cccc returned malformed functions for {relative}")
        for function in functions:
            walk(function)
    return rows


def _cccc_worst(rows: list[tuple[int, int, int]]) -> tuple[int, int]:
    return max(cyclomatic for cyclomatic, _, _ in rows), max(
        cognitive for _, cognitive, _ in rows
    )


def _cccc_regressed(current: tuple[int, int], prior: tuple[int, int]) -> bool:
    """Return whether either complexity axis increased."""

    return current[0] > prior[0] or current[1] > prior[1]


def _run_cccc(config: dict[str, Any], paths: list[str]) -> int:
    selected = _source_paths(paths)
    if not selected and ".cccc.toml" not in paths:
        print("cccc gate: no changed supported source files")
        return 0
    if not CCCC_CONFIG.is_file():
        _fail(f"missing {CCCC_CONFIG}; refusing unconfigured complexity defaults")
    cccc_policy = _read_toml(CCCC_CONFIG)
    if cccc_policy.get("max-cyclomatic") != config["cccc_max_cyclomatic"]:
        _fail(".cccc.toml max-cyclomatic disagrees with the scanner profile")
    if cccc_policy.get("max-cognitive") != config["cccc_max_cognitive"]:
        _fail(".cccc.toml max-cognitive disagrees with the scanner profile")
    executable = _tool("cccc", "CCCC_BIN", config)
    _verify_version(executable, config["cccc_version"], "cccc")
    # The changed-source rule is a live delta, not a permanent debt baseline:
    # new functions over either cap fail, existing functions that get worse
    # fail, and untouched pre-existing over-cap functions remain visible but do
    # not block an unrelated edit. This keeps adoption possible while the
    # release/CI census drives the historical count toward zero.
    violations: list[tuple[str, str, str, int, tuple[int, int], tuple[int, int]]] = []
    rows = 0
    over_cap = 0
    with tempfile.TemporaryDirectory(prefix="scanner-cccc-") as temporary:
        directory = Path(temporary)
        for relative in selected:
            after_path = _materialise_staged(relative, directory / "after")
            if after_path is None:
                continue
            after_rows = _cccc_rows(executable, after_path, relative)
            before_blob = _reference_blob("HEAD", relative)
            before_rows: dict[str, list[tuple[int, int, int]]] = {}
            if before_blob is not None:
                before_path = _materialise_blob(
                    before_blob, relative, directory / "before"
                )
                before_rows = _cccc_rows(executable, before_path, relative)

            rows += sum(len(functions) for functions in after_rows.values())
            for name, current in after_rows.items():
                current_worst = _cccc_worst(current)
                over_cap += sum(
                    1
                    for cyclomatic, cognitive, _ in current
                    if cyclomatic > config["cccc_max_cyclomatic"]
                    or cognitive > config["cccc_max_cognitive"]
                )
                prior = before_rows.get(name)
                if prior is None:
                    for cyclomatic, cognitive, line in current:
                        if (
                            cyclomatic > config["cccc_max_cyclomatic"]
                            or cognitive > config["cccc_max_cognitive"]
                        ):
                            violations.append(
                                (
                                    "NEW",
                                    relative,
                                    name,
                                    line,
                                    (0, 0),
                                    (cyclomatic, cognitive),
                                )
                            )
                elif _cccc_regressed(current_worst, _cccc_worst(prior)):
                    line = max(current, key=lambda row: (row[0], row[1]))[2]
                    violations.append(
                        (
                            "WORSE",
                            relative,
                            name,
                            line,
                            _cccc_worst(prior),
                            current_worst,
                        )
                    )
    print(
        f"cccc gate: {rows} changed function row(s), {over_cap} currently "
        f"over {config['cccc_max_cyclomatic']}/{config['cccc_max_cognitive']}; "
        f"{len(violations)} new/regressed"
    )
    for kind, relative, name, line, before, after in violations:
        if kind == "NEW":
            print(
                f"  NEW {relative}:{line} {name}: cyclomatic={after[0]}, "
                f"cognitive={after[1]}"
            )
        else:
            print(
                f"  WORSE {relative}:{line} {name}: "
                f"cyclomatic={before[0]}->{after[0]}, "
                f"cognitive={before[1]}->{after[1]}"
            )
    return 1 if violations else 0


def _run_cccc_census(config: dict[str, Any]) -> int:
    """Fail when any current tracked source function exceeds either cap."""

    selected = _all_source_paths()
    if not selected:
        print("cccc census: no tracked supported source files")
        return 0
    if not CCCC_CONFIG.is_file():
        _fail(f"missing {CCCC_CONFIG}; refusing unconfigured complexity defaults")
    cccc_policy = _read_toml(CCCC_CONFIG)
    if cccc_policy.get("max-cyclomatic") != config["cccc_max_cyclomatic"]:
        _fail(".cccc.toml max-cyclomatic disagrees with the scanner profile")
    if cccc_policy.get("max-cognitive") != config["cccc_max_cognitive"]:
        _fail(".cccc.toml max-cognitive disagrees with the scanner profile")
    executable = _tool("cccc", "CCCC_BIN", config)
    _verify_version(executable, config["cccc_version"], "cccc")
    rows = 0
    violations: list[tuple[str, str, int, int, int]] = []
    with tempfile.TemporaryDirectory(prefix="scanner-cccc-census-") as temporary:
        directory = Path(temporary)
        for relative in selected:
            source = _materialise_staged(relative, directory / "current")
            if source is None:
                continue
            functions = _cccc_rows(executable, source, relative)
            rows += sum(len(items) for items in functions.values())
            for name, items in functions.items():
                for cyclomatic, cognitive, line in items:
                    if (
                        cyclomatic > config["cccc_max_cyclomatic"]
                        or cognitive > config["cccc_max_cognitive"]
                    ):
                        violations.append((relative, name, line, cyclomatic, cognitive))
    print(
        f"cccc census: {rows} function row(s), {len(violations)} over "
        f"{config['cccc_max_cyclomatic']}/{config['cccc_max_cognitive']}"
    )
    for relative, name, line, cyclomatic, cognitive in violations:
        print(
            f"  OVER {relative}:{line} {name}: cyclomatic={cyclomatic}, "
            f"cognitive={cognitive}"
        )
    return 1 if violations else 0


def _run_kiss_census(config: dict[str, Any]) -> int:
    """Run the full-tree KISS check through the generated shell contract."""

    script = ROOT / "scripts" / "run_kiss.sh"
    if not script.is_file():
        _fail(f"missing {script}; refusing an unconfigured KISS census")
    if not os.access(script, os.R_OK):
        _fail(f"cannot read {script}; refusing a KISS census")
    # The shell wrapper owns KISS's policy grammar and output contract.  Keep
    # the version in the Python profile checked here so a missing or drifted
    # binary cannot be mistaken for a successful census.
    executable = _tool("kiss", "KISS_BIN", config)
    _verify_version(executable, config["kiss_version"], "kiss")
    environment = os.environ.copy()
    environment["KISS_BIN"] = executable
    try:
        result = subprocess.run(
            ["bash", str(script), "--census"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
            env=environment,
        )
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        _fail(f"KISS census could not run: {exc}")
    if result.stdout:
        print(result.stdout, end="")
    if result.returncode == 0:
        return 0
    if result.returncode == 1:
        return 1
    _fail(f"KISS census exited {result.returncode}: {(result.stderr or '')[:400]}")


def _dupehound_findings(document: object) -> list[dict[str, Any]]:
    if (
        not isinstance(document, dict)
        or not isinstance(document.get("schema_version"), int)
        or isinstance(document.get("schema_version"), bool)
        or document.get("schema_version") != 1
    ):
        _fail("dupehound JSON schema drift or non-object result")
    findings = document.get("findings")
    if not isinstance(findings, list):
        _fail("dupehound JSON result has no findings array")
    required = (
        "file",
        "line",
        "name",
        "similarity",
        "original_file",
        "original_line",
        "original_name",
    )
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            _fail(f"dupehound finding {index} is not an object")
        missing = [field for field in required if field not in finding]
        if missing:
            _fail(f"dupehound finding {index} is missing {', '.join(missing)}")
        for field in ("file", "name", "original_file", "original_name"):
            if not isinstance(finding[field], str) or not finding[field].strip():
                _fail(f"dupehound finding {index} has an invalid {field}")
        for field in ("line", "original_line"):
            if (
                isinstance(finding[field], bool)
                or not isinstance(finding[field], int)
                or finding[field] <= 0
            ):
                _fail(f"dupehound finding {index} has an invalid {field}")
        similarity = finding["similarity"]
        if isinstance(similarity, bool) or not isinstance(similarity, (int, float)):
            _fail(f"dupehound finding {index} has an invalid similarity")
        try:
            similarity_value = float(similarity)
        except (OverflowError, ValueError):
            _fail(f"dupehound finding {index} has an invalid similarity")
        if not math.isfinite(similarity_value) or not 0.0 <= similarity_value <= 1.0:
            _fail(f"dupehound finding {index} has an invalid similarity")
    return findings


def _run_dupehound(config: dict[str, Any], paths: list[str]) -> int:
    selected = _source_paths(paths)
    if not selected:
        print("dupehound gate: no changed supported-language function")
        return 0
    executable = _tool("dupehound", "DUPEHOUND_BIN", config)
    _verify_version(executable, config["dupehound_version"], "dupehound")
    command = [
        executable,
        "check",
        "--json",
        "--threshold",
        str(config["dupehound_threshold"]),
        "--min-tokens",
        str(config["dupehound_min_tokens"]),
        "--include-tests",
        *(
            argument
            for pattern in EXCLUDED_GLOBS
            for argument in ("--exclude", pattern)
        ),
        str(ROOT),
    ]
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        _fail(f"dupehound could not run: {exc}")
    if result.returncode not in {0, 1}:
        _fail(
            f"dupehound exited {result.returncode}: {(result.stderr or '').strip()[:400]}"
        )
    try:
        findings = _dupehound_findings(json.loads(result.stdout or ""))
    except json.JSONDecodeError as exc:
        _fail(f"dupehound returned invalid JSON: {exc}")
    if result.returncode == 0 and findings:
        _fail("dupehound returned findings with exit 0")
    if result.returncode == 1 and not findings:
        _fail("dupehound returned exit 1 without findings")
    if findings:
        print(f"dupehound gate: FAIL — {len(findings)} duplicate function(s)")
        for finding in findings:
            print(
                f"  {finding['file']}:{finding['line']} {finding['name']}() "
                f"duplicates {finding['original_file']}:{finding['original_line']} "
                f"{finding['original_name']}()"
            )
        return 1
    print("dupehound gate: PASS — no new duplicate functions")
    return 0


def _archive(ref: str, destination: Path) -> None:
    try:
        result = subprocess.run(
            ["git", "archive", ref],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        _fail(f"could not archive {ref}: {exc}")
    if result.returncode != 0:
        _fail(
            f"git archive {ref} failed: {(result.stderr or b'').decode(errors='replace')[:400]}"
        )
    destination.mkdir(parents=True, exist_ok=True)
    try:
        with tarfile.open(fileobj=BytesIO(result.stdout), mode="r:") as archive:
            root = destination.resolve()
            for member in archive.getmembers():
                target = (destination / member.name).resolve()
                if not target.is_relative_to(root):
                    _fail(f"git archive {ref} contained an unsafe path")
                if member.issym() or member.islnk():
                    link_target = (target.parent / member.linkname).resolve()
                    if not link_target.is_relative_to(root):
                        _fail(
                            f"git archive {ref} contained a link escaping the scan root"
                        )
            archive.extractall(destination)
    except (OSError, tarfile.TarError) as exc:
        _fail(f"could not unpack git archive {ref}: {exc}")


def _scan_targets(root: Path) -> list[Path]:
    """Decompose a live git root so native tools never walk `.git`."""

    targets: list[Path] = []
    for child in sorted(root.iterdir()):
        if child.name == ".git" or child.name in EXCLUDED_DIRECTORY_NAMES:
            continue
        targets.append(child)
    return targets or [root]


def _guard_jscpd_config(root: Path) -> None:
    """Reject jscpd's cwd-discovered policy files before invoking it."""

    for name in sorted(JSCPD_CONFIG_NAMES):
        candidate = root / name
        if candidate.exists():
            _fail(
                f"{candidate} exists; jscpd auto-loads it from the current "
                "working directory and could silently override the pinned "
                "scanner policy"
            )


def _jscpd_report(
    executable: str, root: Path, report_directory: Path, config: dict[str, Any]
) -> dict[str, Any]:
    _guard_jscpd_config(root)
    targets = _scan_targets(root) if (root / ".git").exists() else [root]
    if not targets:
        _fail("jscpd resolved no scan targets")
    command = [
        executable,
        "--min-tokens",
        str(config["jscpd_min_tokens"]),
        "--min-lines",
        str(config["jscpd_min_lines"]),
        "--mode",
        config["jscpd_mode"],
        "--ignore",
        ",".join(EXCLUDED_GLOBS),
        "--absolute",
        "-r",
        "json",
        "-o",
        str(report_directory),
        "--silent",
        "--no-tips",
        *(str(target) for target in targets),
    ]
    try:
        result = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        _fail(f"jscpd could not run: {exc}")
    if result.returncode != 0:
        _fail(f"jscpd exited {result.returncode}: {(result.stdout or '')[-500:]}")
    report = report_directory / "jscpd-report.json"
    if not report.is_file():
        _fail(f"jscpd exited 0 but wrote no report at {report}")
    try:
        document = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail(f"jscpd report is not valid JSON: {exc}")
    if not isinstance(document, dict) or not isinstance(
        document.get("duplicates"), list
    ):
        _fail("jscpd report has no duplicates array")
    for index, clone in enumerate(document["duplicates"]):
        if not isinstance(clone, dict):
            _fail(f"jscpd duplicate {index} is not an object")
        for field in (
            "format",
            "fragment",
            "lines",
            "tokens",
            "firstFile",
            "secondFile",
        ):
            if field not in clone:
                _fail(f"jscpd duplicate {index} is missing {field}")
        if (
            not isinstance(clone["format"], str)
            or not isinstance(clone["fragment"], str)
            or isinstance(clone["lines"], bool)
            or not isinstance(clone["lines"], int)
            or clone["lines"] <= 0
            or isinstance(clone["tokens"], bool)
            or not isinstance(clone["tokens"], int)
            or clone["tokens"] <= 0
        ):
            _fail(f"jscpd duplicate {index} has invalid format/size fields")
        for side in ("firstFile", "secondFile"):
            location = clone[side]
            if not isinstance(location, dict) or not isinstance(
                location.get("name"), str
            ):
                _fail(f"jscpd duplicate {index} has an invalid {side}")
            for point in ("startLoc", "endLoc"):
                position = location.get(point)
                if not isinstance(position, dict):
                    _fail(f"jscpd duplicate {index} has an invalid {side}.{point}")
                line = position.get("line")
                if isinstance(line, bool) or not isinstance(line, int) or line <= 0:
                    _fail(f"jscpd duplicate {index} has an invalid {side}.{point}.line")
    return document


def _relative_report_path(value: str, root: Path) -> str:
    path = Path(value)
    try:
        if path.is_absolute():
            path = path.relative_to(root)
    except ValueError:
        _fail(f"jscpd report path escaped its scan root: {value!r}")
    return _normalise(str(path))


def _clone_key(clone: dict[str, Any], root: Path) -> tuple[Any, ...]:
    first = clone["firstFile"]
    second = clone["secondFile"]
    # Line ranges are presentation data, not identity: inserting an unrelated
    # line before an old clone must not turn unchanged debt into a NEW clone.
    # The fragment digest plus the unordered file pair remains stable across
    # line shifts in either file.
    pair = frozenset(
        {
            _relative_report_path(first["name"], root),
            _relative_report_path(second["name"], root),
        }
    )
    digest = hashlib.sha256(
        clone["fragment"].encode("utf-8", "surrogatepass")
    ).hexdigest()
    return (
        clone["format"],
        digest,
        pair,
    )


def _clone_touches_changed(
    clone: dict[str, Any], root: Path, changed: set[str]
) -> bool:
    return any(
        _relative_report_path(clone[side]["name"], root) in changed
        for side in ("firstFile", "secondFile")
    )


def _run_jscpd(
    config: dict[str, Any],
    paths: list[str],
    base_ref: str | None = None,
    target_ref: str = "HEAD",
) -> int:
    _guard_jscpd_config(ROOT)
    changed = set(_jscpd_paths(paths))
    if not changed:
        print("jscpd gate: no changed code/template/config files")
        return 0
    executable = _tool("jscpd", "JSCPD_BIN", config)
    _verify_version(executable, config["jscpd_version"], "jscpd")
    base_ref = base_ref or os.environ.get("CX_SCANNER_BASE_REF", "main")
    target_ref = target_ref or os.environ.get("CX_SCANNER_TARGET_REF", "HEAD")
    with tempfile.TemporaryDirectory(prefix="scanner-jscpd-") as temporary:
        temporary_root = Path(temporary)
        before_root = temporary_root / "before"
        after_root = temporary_root / "after"
        _archive(base_ref, before_root)
        _archive(target_ref, after_root)
        before_report = _jscpd_report(
            executable, before_root, temporary_root / "before-report", config
        )
        after_report = _jscpd_report(
            executable, after_root, temporary_root / "after-report", config
        )
        before_keys = {
            _clone_key(clone, before_root) for clone in before_report["duplicates"]
        }
        new_clones = [
            clone
            for clone in after_report["duplicates"]
            if _clone_key(clone, after_root) not in before_keys
            and _clone_touches_changed(clone, after_root, changed)
            and not _excluded(
                _relative_report_path(clone["firstFile"]["name"], after_root)
            )
            and not _excluded(
                _relative_report_path(clone["secondFile"]["name"], after_root)
            )
        ]
    if new_clones:
        print(f"jscpd gate: FAIL — {len(new_clones)} new clone(s)")
        for clone in new_clones:
            first = clone["firstFile"]
            second = clone["secondFile"]
            print(
                f"  {clone['format']} {clone['lines']}L/{clone['tokens']}tok: "
                f"{_relative_report_path(first['name'], after_root)}:"
                f"{first['startLoc']['line']} <-> "
                f"{_relative_report_path(second['name'], after_root)}:"
                f"{second['startLoc']['line']}"
            )
        return 1
    print("jscpd gate: PASS — no new code/template/config blocks")
    return 0


def _run_jscpd_census(config: dict[str, Any]) -> int:
    executable = _tool("jscpd", "JSCPD_BIN", config)
    _verify_version(executable, config["jscpd_version"], "jscpd")
    with tempfile.TemporaryDirectory(prefix="scanner-jscpd-census-") as temporary:
        report = _jscpd_report(executable, ROOT, Path(temporary), config)
        duplicates = report["duplicates"]
        print(
            f"jscpd census: {len(duplicates)} clone(s) across the full "
            "code/template/config tree (advisory findings)"
        )
    return 0


def _jscpd_range() -> tuple[str, str]:
    """Resolve the push range that pre-commit exposes to pre-push hooks.

    A real pre-push invocation gets PRE_COMMIT_FROM_REF/TO_REF. Manual runs
    have neither, so they intentionally compare the current HEAD with `main`
    (or an explicit CX_SCANNER_BASE_REF) and fail closed if that ref is absent.
    """

    base_ref = os.environ.get("CX_SCANNER_BASE_REF") or os.environ.get(
        "PRE_COMMIT_FROM_REF"
    )
    target_ref = os.environ.get("CX_SCANNER_TARGET_REF") or os.environ.get(
        "PRE_COMMIT_TO_REF"
    )
    return base_ref or "main", target_ref or "HEAD"


def _run_import_linter(config: dict[str, Any], paths: list[str]) -> int:
    if not _python_paths(paths) and ".importlinter" not in paths:
        print("import-linter gate: no changed Python modules")
        return 0
    if not IMPORTLINTER_CONFIG.is_file():
        _fail(
            f"missing {IMPORTLINTER_CONFIG}; refusing an unconfigured architecture check"
        )
    executable = _tool("lint-imports", "IMPORT_LINTER_BIN", config)
    _verify_version(executable, config["import_linter_version"], "import-linter")
    try:
        result = subprocess.run(
            [executable, "--config", str(IMPORTLINTER_CONFIG)],
            cwd=ROOT,
            text=True,
            check=False,
            timeout=300,
        )
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        _fail(f"import-linter could not run: {exc}")
    if result.returncode not in {0, 1}:
        _fail(f"import-linter exited {result.returncode}")
    if result.returncode:
        print("import-linter gate: FAIL — architecture contract violation")
        return 1
    print("import-linter gate: PASS — package architecture contracts hold")
    return 0


def _dispatch(mode: str) -> int:
    config = _scanner_config()
    if mode == "cccc-census":
        return _run_cccc_census(config)
    if mode == "kiss-census":
        return _run_kiss_census(config)
    if mode == "jscpd-census":
        return _run_jscpd_census(config)
    if mode == "jscpd":
        base_ref, target_ref = _jscpd_range()
        paths = changed_paths(base_ref, target_ref)
        return _run_jscpd(config, paths, base_ref, target_ref)
    paths = changed_paths()
    if mode == "cccc":
        return _run_cccc(config, paths)
    if mode == "dupehound":
        return _run_dupehound(config, paths)
    if mode == "import-linter":
        return _run_import_linter(config, paths)
    _fail(f"unknown scanner mode: {mode}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode",
        choices=(
            "cccc",
            "cccc-census",
            "dupehound",
            "jscpd",
            "jscpd-census",
            "kiss-census",
            "import-linter",
        ),
    )
    try:
        return _dispatch(parser.parse_args().mode)
    except ScannerError as exc:
        print(f"scanner gate: CANNOT RUN: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
