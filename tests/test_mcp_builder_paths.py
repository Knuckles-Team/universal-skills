"""Relative scaffold paths must complete the same readiness contract."""

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts/scaffold_package.py"
)


@pytest.mark.parametrize("output", [None, ".", "nested/output"])
@pytest.mark.parametrize("in_place", [False, True])
def test_relative_output_completes_readiness(tmp_path, output, in_place):
    command = [sys.executable, str(SCRIPT), "relative-example"]
    if output is not None:
        command.extend(["--output-dir", output])
    if in_place:
        command.append("--in-place")
    result = subprocess.run(
        command, cwd=tmp_path, capture_output=True, text=True, timeout=30, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    root = tmp_path / (output or ".")
    if not in_place:
        root /= "relative-example"
    assert (root / "requirements.txt").is_file()
    assert (root / "llms.txt").is_file()
    assert (root / "agent-readiness-manifest.json").is_file()
    checked = subprocess.run(
        [
            sys.executable,
            str(root / "scripts/generate_agent_readiness.py"),
            "--root",
            str(root),
            "--check",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert checked.returncode == 0, checked.stdout + checked.stderr
