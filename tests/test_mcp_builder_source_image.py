"""Source image inputs must come from the generated checkout, including runtime data."""
from __future__ import annotations

import configparser
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "universal_skills/agent-tools/mcp-builder/scripts/check_tool_parity.py"














def test_parity_rejects_undeclared_no_binary(tmp_path):
    spec = importlib.util.spec_from_file_location("parity_check", SCRIPT)
    parity = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parity)
    (tmp_path / "docker").mkdir()
    docker = tmp_path / "docker/Dockerfile"
    docker.write_text("RUN pip install --only-binary :all: --no-binary pyspark spark-mcp[mcp]==1.0\n")
    assert parity.dockerfile_findings(tmp_path) == [
        "docker/Dockerfile: --no-binary pyspark is not in [tool.pipelines] allow-source-build"
    ]
    (tmp_path / "pyproject.toml").write_text('[tool.pipelines]\nallow-source-build = ["pyspark"]\n')
    assert parity.dockerfile_findings(tmp_path) == []
    docker.write_text("RUN pip install --only-binary :all: --no-binary :all: spark-mcp[mcp]==1.0\n")
    assert parity.dockerfile_findings(tmp_path)


def _parity():
    spec = importlib.util.spec_from_file_location("parity_lost", SCRIPT)
    parity = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parity)
    return parity


def test_parity_fails_on_previous_tools_without_successor(tmp_path):
    parity = _parity()
    previous = {"x_signals", "x_risk", "x_old_tool", "x_get_quote"}
    served = {"x_signals_alpha", "x_risk_kelly", "x_get_quote"}
    assert parity.lost_tools(previous, served, set()) == ["x_old_tool"]
    assert parity.lost_tools(previous, served, {"x_old_tool"}) == []


def test_parity_counts_a_covering_operation_tool_as_successor():
    parity = _parity()
    previous = {"x_branches", "x_branches_get", "x_search_code", "x_gone"}
    served = {"x_get_branch", "x_code_search"}
    report = [
        {"tool": "x_branches", "action": "get", "split": "x_branches_get",
         "outcome": "covered", "served_by": "x_get_branch", "reason": "table"},
        {"tool": "x_search", "action": "code", "split": "x_search_code",
         "outcome": "covered", "served_by": "x_not_served", "reason": "name"},
    ]
    covered = parity.covered_tools(report, served)
    assert covered == {"x_branches", "x_branches_get"}
    assert parity.lost_tools(previous, served, set(), covered) == ["x_gone", "x_search_code"]


def test_parity_reads_declared_retired_tools(tmp_path):
    parity = _parity()
    assert parity.declared_retired_tools(tmp_path) == set()
    (tmp_path / "pyproject.toml").write_text('[tool.pipelines]\nretired-tools = ["x_old_tool"]\n')
    assert parity.declared_retired_tools(tmp_path) == {"x_old_tool"}
