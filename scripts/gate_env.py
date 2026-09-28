#!/usr/bin/env python3
"""Run a gate command, or report why it cannot run here.

A fresh clone may lack a tool or the locked project environment that
``scripts/bootstrap.sh`` creates. Such a gate has found nothing, so it must not
report a pass -- but it must not block a contributor's commit either:

* locally it prints ``SKIPPED (<gate>): <reason>`` and exits 0;
* in CI (``CI`` set) it prints ``CANNOT RUN`` and exits 2, because CI runs
  ``scripts/bootstrap.sh`` first and is expected to provide everything.

Usage::

    python3 scripts/gate_env.py --gate pytest --project-env -- python -m pytest tests
    python3 scripts/gate_env.py --gate demo --need docker -- docker compose config
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess  # nosec B404 - argv from the hook definition, no shell
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def unavailable(gate: str, reason: str) -> int:
    """Fail closed in CI; skip visibly everywhere else."""

    if os.environ.get("CI"):
        print(f"{gate}: CANNOT RUN in CI: {reason}", file=sys.stderr)
        return 2
    print(f"SKIPPED ({gate}): {reason}")
    return 0


def project_bin() -> Path:
    """The scripts directory of the locked ``.venv`` bootstrap syncs."""

    return ROOT / ".venv" / ("Scripts" if os.name == "nt" else "bin")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--gate", required=True)
    parser.add_argument("--need", action="append", default=[], metavar="TOOL")
    parser.add_argument(
        "--project-env",
        action="store_true",
        help="run inside the locked .venv (its bin directory leads PATH)",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER)
    options = parser.parse_args(argv)
    command = options.command[1:] if options.command[:1] == ["--"] else options.command
    if not command:
        parser.error("a command is required after --")

    environment = os.environ.copy()
    if options.project_env:
        venv_bin = project_bin()
        if not venv_bin.is_dir():
            return unavailable(
                options.gate, "no project environment; run scripts/bootstrap.sh"
            )
        environment.pop("PYTHONPATH", None)
        environment["VIRTUAL_ENV"] = str(venv_bin.parent)
        environment["PATH"] = os.pathsep.join([str(venv_bin), environment["PATH"]])
    for tool in options.need:
        if shutil.which(tool, path=environment["PATH"]) is None:
            return unavailable(options.gate, f"`{tool}` is not installed")
    resolved = shutil.which(command[0], path=environment["PATH"]) or command[0]
    return subprocess.run(  # nosec B603
        [resolved, *command[1:]], cwd=ROOT, env=environment
    ).returncode


if __name__ == "__main__":
    sys.exit(main())
